# ③ 确认维度（Kimball Step 3）

从每个业务过程中提取维度引用，收敛一致性维度，确认退化维度与低基数离散属性，确定 SCD 策略。

---

## 1. 输入

| 输入项 | 来源 Skill | 过滤条件 | 用途 |
|--------|-----------|---------|------|
| `dwm_bp_business_process` | ② | 全量 | 业务过程清单与粒度声明 |
| `dwm_inv_field_profile` | ① | `field_role='foreign_key'` | 维度外键引用（含 `ref_table`/`ref_column`/`join_miss_rate`） |
| `dwm_inv_field_profile` | ① | `field_role='low_cardinality'` | 低基数离散属性候选（Junk Dimension 候选） |
| `dwm_inv_field_profile` | ① | `field_role='primary_key'` | 维度表粒度键候选 |
| `dwm_bp_subject_area` | ② | 全量 | 主题域定义 |

---

## 2. 实施步骤

### 2.1 硬门禁：技术字段排除

在所有维度提取操作前先执行技术字段剔除：

**`field_role IN ('tech_meta')` 的字段全部排除**，不得进入维度候选池。

这包括：ETL 时间戳、同步标记、分区字段（`dt`）、操作类型、批次 ID 等。排除后保留技术相关画像属性供审计，但不建模。

### 2.2 退化维度判定

退化维度是位于事实表中的交易凭证/业务单号，不单独建维表，保留在事实表供追踪。

判定规则（需满足全部条件）：
1. 字段所在表为 `dwm_bp_business_process` 中的业务过程表
2. `field_role` 为 `primary_key` 且 `is_surrogate='N'`（天然业务键），或字段命名含有业务单号语义（`*_no`、`*_order_id`、`invoice_*`）
3. 无需以此字段为主键单独建维表分析其属性

判定为退化维度的字段不进入 `dwm_dim_registry`，在组装阶段由 `dwm_inv_field_profile` 直接推导。

### 2.3 提取维度外键引用

对每个业务过程（`dwm_bp_business_process` 中的每一行）：

1. 从 `dwm_inv_field_profile WHERE field_role='foreign_key'` 提取该事实表的外键字段
2. 通过 `ref_table` / `ref_column` 关联到维度候选表（从 `dwm_inv_field_profile` FK 被引用关系识别）
3. 补充"是否必选维度"与"缺失容忍策略"（如匿名用户→ UNKNOWN 填充）
4. 提取退化维度字段（按 §2.2 规则）
5. 提取低基数离散属性（`field_role='low_cardinality'`），判断是独立 Junk Dimension 还是内联属性
6. 汇总分析结果，仅将需建 DIM 表的维度注册到 `dwm_dim_registry`

### 2.4 收敛一致性维度

1. 汇总所有业务过程外键，去重得到一致性维度候选列表
2. 为每个维度键确定唯一维表来源（从 `dwm_inv_field_profile` FK 被引用关系识别维度候选表）
3. 执行一致性检查：命名、口径、编码、值域、JOIN 命中率
4. 退化维度与低基数离散属性由组装阶段从 `dwm_inv_field_profile` 推导，**不纳入** `dwm_dim_registry`
5. 仅注册需建 DIM 表的一致性维度

### 2.5 确认 SCD 策略

对 `dwm_dim_registry` 中的每个一致性维度，检查其属性字段中是否有可能随时间变化的属性（用户级别、组织名称等）：

| SCD 类型 | 策略 | 适用场景 |
|---------|------|---------|
| `SCD1` | 覆盖写入 | 无需保留历史，直接更新 |
| `SCD2` | 追加行 | 需保留完整历史变化轨迹（`dw_start_date`/`dw_end_date`/`dw_is_current` 由 ETL 生成） |
| `SCD3` | 追加列 | 仅保留前一个值（`prev_xxx` 字段） |

规则：
- 同一维度内不同属性可有不同 SCD 类型（如 `user_name` 用 SCD1，`user_level` 用 SCD2）
- `scd_strategy` 取该维度中最严格的类型
- `scd_columns` 按 `类型:字段` 格式分组记录，如 `SCD2:user_level,org_name;SCD1:phone`
- 无变化属性的维度 `scd_strategy='-'`，`scd_columns` 留空

> 如需编写一致性校验 SQL 或 SCD 维度加工脚本，use context7 获取对应 SparkSQL/HiveQL 的最新文档。

---

## 3. 产出物

### 3.1 `dwm_dim_registry`（一致性维度注册表）

一行一个一致性维度（需建 DIM 表的维度）。产出格式：CSV，路径 `output/dwm-bus-matrix/dimension/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| 维度编码 | 维度唯一标识 | 是 | 主键，命名格式：`dim_xxx` |
| 维度中文名称 | 中文名 | 是 | 如"用户维度" |
| 维度描述 | 一句话业务含义 | 是 | 描述维度用途 |
| 来源ODS表 | 源维表名 | 是 | 从 `dwm_inv_field_profile` FK 被引用关系识别 |
| 粒度键 | 业务键/代理键 | 是 | 逗号分隔 |
| 维度属性字段 | 所有维度属性 | 是 | 逗号分隔 |
| 建模策略 | 建模方式 | 是 | `独立维表` |
| SCD策略 | 维度级SCD类型 | 条件 | 取最严格类型：`SCD1` / `SCD2` / `SCD3` / `-` |
| SCD字段分组 | 按SCD类型分组的字段 | 条件 | `SCD策略 != '-'` 时必填，格式：`SCD2:col1,col2;SCD1:col3` |
| 关联字段 | 事实表JOIN此维度的字段 | 是 | 通常为粒度键 |
| 是否一致性维度 | 跨事实表共享 | 是 | `Y` / `N` |
| 跨事实表共享范围 | 共享说明 | 条件 | `是否一致性维度='Y'` 时必填，列出关联的业务过程英文名称 |
| 备注 | 额外说明 | 否 | |
| 更新时间 | 最近修改时间 | 是 | ISO 日期 |

> 主键：`维度编码`
>
> **说明**：维度引用关系（哪个事实表引用哪个维度、退化维度、低基数属性）在组装阶段从 `dwm_inv_field_profile` 推导，不单独持久化。

---

## 4. 验收标准

1. `dwm_dim_registry` 中每个维度键有唯一口径定义，跨事实无冲突
2. 维度候选池已剔除技术属性字段（`field_role='tech_meta'` 占比 = 0）
3. 每个一致性维度中的 SCD 属性字段已确认 SCD 类型，`SCD字段分组` 格式正确
4. 每个业务过程至少有一个核心分析维度（可从 `dwm_inv_field_profile` FK 关系验证）

---

## 5. 与下游衔接

| 下游 Skill | 消费数据 | 用途 |
|-----------|---------|------|
| ⑤ dwm-matrix | `dwm_dim_registry` | 总线矩阵列头 + DIM 维度表建设清单合成 |
| ⑤ dwm-matrix | `dwm_inv_field_profile`（FK 关系） | 总线矩阵格子填充（从 FK ref_table 映射到 dim_registry）、DWD 字段汇总（退化维度/低基数属性直接从 field_profile 推导） |

---

## 6. 代码规范

### CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

### 读取上游产出示例

```python
# 读取业务过程清单
business_processes = read_csv("output/dwm-bus-matrix/business-process/dwm_bp_business_process.csv")

# 读取字段外键画像
field_profile = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv")
fk_fields = [f for f in field_profile if f["field_role"] == "foreign_key"]

# 读取低基数候选
lc_fields = [f for f in field_profile if f["field_role"] == "low_cardinality"]
```

### 一致性检查 SQL

> 如需编写跨事实表维度一致性校验脚本，use context7 获取 SQL 方言文档。

```sql
-- 同一维度键在不同事实表中 JOIN 命中率对比
SELECT
  a.fact_table,
  a.dimension_column,
  a.ref_table,
  COUNT(1) AS ref_cnt,
  SUM(CASE WHEN b.ref_col IS NULL THEN 1 ELSE 0 END) AS miss_cnt,
  ROUND(SUM(CASE WHEN b.ref_col IS NULL THEN 1 ELSE 0 END) / COUNT(1), 4) AS miss_rate
FROM fact_ods_table a
LEFT JOIN dim_ods_table b ON a.fk_col = b.ref_col
WHERE a.fk_col IS NOT NULL
  AND a.dt = '${check_dt}'
GROUP BY a.fact_table, a.dimension_column, a.ref_table;
```
