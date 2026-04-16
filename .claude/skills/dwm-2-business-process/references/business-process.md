# ② 选择业务过程 + 声明粒度（Kimball Step 1+2）

通过表关系网识别业务过程（总线矩阵的行），同步完成主题域定义与粒度声明——不声明粒度的业务过程识别没有意义。

---

## 1. 输入

| 输入项 | 来源 Skill | 过滤条件 | 用途 |
|--------|-----------|---------|------|
| `dwm_inv_field_profile` | ① | `field_role IN ('primary_key','foreign_key','business_time','numeric_measure')` | 画表关系图的核心证据 |
| `dwm_inv_field_profile` | ① | `field_role='foreign_key'` | 外键关系连线（含 `ref_table`/`ref_column`/`join_miss_rate`） |
| `dwm_inv_field_registry` | ① | `constraint_type IN ('PK','UK','FK')` | 源系统约束，最高优先级证据 |
| `dwm_inv_ods_inventory` | ① | 全量 | ODS 表清单、同步模式、行数 |

---

## 2. 接口数据无主键降级策略

接口数据（API/文件/消息队列）通常无 PK/FK 约束，① 完整度等级为"缺失/部分"时，在本步骤通过数据画像补充证据。

| 场景 | 降级处理 | 操作方法 |
|------|---------|---------|
| 无主键 | 画像发现天然业务键 | 候选列 `distinct_rate ≥ 99.9%` + `null_rate ≤ 1%` → 业务键候选 |
| 无外键约束 | JOIN 命中率发现关系 | 候选字段 LEFT JOIN 目标表，`miss_rate ≤ 1%` → 外键候选 |
| 联合键才唯一 | 逐步增加组合字段 | 找满足唯一性的最小字段集 → 粒度键 |
| 同名字段无约束 | 值域匹配作弱证据 | 类型一致 + 值域重叠度 > 95% → 候选关系，需人工确认 |

> 如需编写画像 SQL（唯一率分析、JOIN 命中率分析），use context7 获取对应 SQL 方言的最新文档。

**降级分析 SQL 模板**：

```sql
-- 唯一率分析（发现天然业务键）
SELECT
  COUNT(*) AS total,
  COUNT(DISTINCT candidate_col) AS distinct_cnt,
  ROUND(COUNT(DISTINCT candidate_col) / COUNT(*), 6) AS distinct_rate,
  SUM(CASE WHEN candidate_col IS NULL THEN 1 ELSE 0 END) AS null_cnt
FROM ods_xxx
WHERE dt BETWEEN '${start_dt}' AND '${end_dt}';

-- JOIN 命中率分析（发现外键关系）
SELECT
  COUNT(1) AS ref_cnt,
  SUM(CASE WHEN b.target_col IS NULL THEN 1 ELSE 0 END) AS miss_cnt,
  ROUND(SUM(CASE WHEN b.target_col IS NULL THEN 1 ELSE 0 END) / COUNT(1), 4) AS miss_rate
FROM ods_source a
LEFT JOIN ods_target b ON a.source_col = b.target_col
WHERE a.source_col IS NOT NULL
  AND a.dt BETWEEN '${start_dt}' AND '${end_dt}';
```

---

## 3. 实施步骤

### 3.1 画表关系图（手段，非独立交付）

1. 以 `dwm_inv_field_profile WHERE field_role='foreign_key'` 为主线画连线（不是仅靠同名字段）
2. 以 `dwm_inv_field_registry WHERE constraint_type='FK'` 补充强证据
3. 对同名 ID 做补充候选，再做语义核验（实体含义、值域、JOIN 命中率）
4. 区分角色：
   - **主表**：被引用为主、实体属性稳定 → 维度候选
   - **引用表**：引用多个实体且承载行为 → 事实候选
5. 接口数据补充：对 ① 标记为"缺失/部分"的数据源，通过 §2 降级策略补充外键关系

### 3.2 表角色判定

逐表按四类证据综合评估，判定为 `fact` / `dimension` / `config` / `exclude`：

| 证据类型 | 说明 | 适用判定 |
|---------|------|---------|
| **时间证据** | 表中存在 `field_role=business_time` 的字段 | 事实候选 |
| **度量证据** | 表中存在 `field_role=numeric_measure` 且有多个 | 事实候选 |
| **关联证据** | 表中存在 ≥ 2 个 `field_role=foreign_key` | 事实候选 |
| **增长证据** | `sync_mode=INCR` + 行数远大于其他表 | ���实候选 |

判定规则：
- `fact`：满足 ≥ 2 条事实证据，代表一个业务过程
- `dimension`：被多表引用、实体属性稳定、无度量或度量极少
- `config`：系统配置/参数/枚举映射表，无业务事件意义，不参与维度建模
- `exclude`：纯技术辅助表（日志、锁表、临时表等）

**无数值但有行为轨迹的表** → `table_role=fact`，`role_evidence` 中注明 factless（下单浏览、签到等）。

### 3.3 识别业务过程并归组主题域

1. 对每张 `table_role=fact` 的表，形成标准业务过程命名（如：下单、支付、退款、浏览）
2. **主题域定义**（先底向上，再顶向下）：
   - 自底向上：按业务过程的实体关系自然聚类
   - 自顶向下：对照企业价值链校验，每个主题域必须有：中文名、英文名、编码（2~3 大写字母）、描述
   - 产出 `dwm_bp_subject_area`
3. **归组**：将每个业务过程归入已定义的主题域（通过 `subject_area_code`）
4. 约束：一个业务过程只能归属一个主题域
5. 主题域归属通过 `dwm_bp_table_profile.subject_area_code` 管理，不回填 ① 产出物

### 3.4 声明粒度

1. 按业务过程写一句话粒度声明（例：一行一笔支付交易）
2. 识别承载粒度的键：主键或联合键
3. 做唯一性校验：`COUNT(*)` 对比 `COUNT(DISTINCT 粒度键)`
4. 若不唯一 → 回退修正：补联合键或下钻到更细明细层
5. 接口数据无主键时：通过 §2 唯一率分析发现天然键或联合键作为粒度键

> 如需编写粒度唯一性批量校验脚本，use context7 获取 SQL 方言文档。

**粒度唯一性校验 SQL**：

```sql
SELECT
  COUNT(*) AS total_row_cnt,
  COUNT(DISTINCT ${grain_key_cols}) AS grain_distinct_cnt
FROM ${ods_table_name}
WHERE dt = '${check_dt}';
-- total_row_cnt = grain_distinct_cnt → 通过
```

---

## 4. 产出物

### 4.1 `dwm_bp_table_profile`（表角色画像表）

一行一张表。产出格式：CSV，路径 `output/dwm-bus-matrix/business-process/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| source_code | 数据源编码 | 是 | 关联 `dwm_inv_source_registry` |
| ods_table_name | ODS 表名 | 是 | 主键 |
| table_role | 表角色 | 是 | `fact` / `dimension` / `config` / `exclude` |
| role_evidence | 角色判定依据 | 是 | 四类证据综合说明 |
| business_process | 业务过程名称 | 条件 | `table_role=fact` 时必填 |
| bp_standard_name | 业务过程标准命名（英文） | 条件 | `table_role=fact` 时必填，如 `order_pay` |
| bp_desc | 业务过程描述 | 条件 | `table_role=fact` 时必填 |
| subject_area_code | 主题域编码 | 条件 | `table_role != 'exclude'` 时必填，关联 `dwm_bp_subject_area` |
| subject_area_basis | 主题域归组依据 | 条件 | `table_role != 'exclude'` 时必填 |
| fact_type | 事实表类型 | 条件 | **④ 回写**：`transaction` / `periodic_snapshot` / `accumulating_snapshot` / `factless` |
| fact_type_evidence | 事实表类型判定依据 | 条件 | **④ 回写** |
| grain_statement | 粒度声明 | 条件 | `table_role IN ('fact','dimension')` 时必填，一句话 |
| grain_keys | 粒度键 | 条件 | `table_role IN ('fact','dimension')` 时必填，逗号分隔 |
| grain_total_count | 校验-总行数 | 条件 | `COUNT(*)` 结果 |
| grain_distinct_count | 校验-去重数 | 条件 | `COUNT(DISTINCT 粒度键)` 结果 |
| grain_check_result | 校验结果 | 条件 | `pass` / `fail` |
| fact_candidate_final | 事实候选最终判定 | 是 | `Y(确认)` / `N` |
| exclude_reason | 排除原因 | 条件 | `table_role=exclude` 时必填 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`ods_table_name`
>
> **回写说明**：`fact_type` 和 `fact_type_evidence` 当步允许为空（待 ④ 回填），回填后须重新检查验收标准 §5.2。

### 4.2 `dwm_bp_subject_area`（主题域注册表）

一行一个主题域。产出格式：CSV，路径 `output/dwm-bus-matrix/business-process/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| subject_area_code | 主题域编码 | 是 | 主键，2~3 大写字母，如 `TRD` |
| subject_area_name_cn | 中文名称 | 是 | 如"交易域" |
| subject_area_name_en | 英文名称 | 是 | 如"Trade" |
| subject_area_desc | 描述 | 是 | 一句话业务范围 |
| business_scope | 业务范围 | 是 | 核心业务活动，逗号分隔 |
| owner | 负责人 | 否 | 主题域业务负责人 |
| definition_basis | 定义依据 | 是 | 自底向上聚类 + 自顶向下校验的结论 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code`
>
> **命名约束**：`subject_area_code` 全局唯一，一经定义不可随意变更（下游 DWD/DWS/ADS 表名依赖此缩写，统一转小写使用）。
>
> **设计原则**：主题域数量控制在 5~10 个；维度表按实体所属域归入，不按引用它的事实表归入。

---

## 5. 验收标准

### 5.1 当步必须完成（进入 ③④ 前）

1. `dwm_bp_table_profile` 当批次每张表有明确 `table_role`
2. 所有 `table_role=fact` 有完整的 `business_process`、`bp_standard_name`、`subject_area_code`、`grain_statement`
3. 所有 `table_role=dimension` 有 `grain_statement` 和 `grain_keys`
4. 粒度键唯一性校验通过（`grain_check_result=pass`）
5. 每个业务过程只归属一个主题域（1:1）
6. `dwm_bp_subject_area` 已定义且外键引用有效
7. 高风险歧义关系（接口数据/无约束外键）已人工确认
8. `fact_type` / `fact_type_evidence` 当步允许为空（待 ④ 回写）

### 5.2 ④ 回写后复验

1. 所有 `table_role=fact` 的 `fact_type` 非空
2. 所有 `fact_type` 非空的记录 `fact_type_evidence` 非空

---

## 6. 与下游衔接

| 下游 Skill | 消费数据 | 用途 |
|-----------|---------|------|
| ③ dwm-3-dimension | `dwm_bp_table_profile WHERE table_role='fact'` | 每个业务过程提取维度引用 |
| ③ dwm-3-dimension | `dwm_bp_table_profile WHERE table_role='dimension'` | 维度候选表与粒度键 |
| ③ dwm-3-dimension | `dwm_bp_subject_area` | 主题域主数据 |
| ④ dwm-4-fact | `dwm_bp_table_profile WHERE table_role='fact'` | 业务过程清单，确定事实表类型与度量归属 |
| ⑤ dwm-5-bus-matrix | `dwm_bp_table_profile` | 矩阵行、粒度、事实表类型 |
| ⑤ dwm-5-bus-matrix | `dwm_bp_subject_area` | 主题域清单合成 |

---

## 7. 派生查询

```sql
-- 维度候选表清单
SELECT p.ods_table_name, p.grain_statement, p.grain_keys,
       s.subject_area_code, s.subject_area_name_cn
FROM dwm_bp_table_profile p
LEFT JOIN dwm_bp_subject_area s ON p.subject_area_code = s.subject_area_code
WHERE p.table_role = 'dimension';

-- 事实候选表清单
SELECT p.ods_table_name, p.business_process, p.bp_standard_name,
       s.subject_area_code, s.subject_area_name_cn
FROM dwm_bp_table_profile p
LEFT JOIN dwm_bp_subject_area s ON p.subject_area_code = s.subject_area_code
WHERE p.table_role = 'fact';

-- 主题域下属业务过程汇总
SELECT s.subject_area_code, s.subject_area_name_cn,
       COUNT(p.ods_table_name) AS fact_count
FROM dwm_bp_subject_area s
LEFT JOIN dwm_bp_table_profile p ON s.subject_area_code = p.subject_area_code
  AND p.table_role = 'fact'
GROUP BY s.subject_area_code, s.subject_area_name_cn;
```

---

## 8. 代码规范

### CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

### 读取上游产出

```python
# 读取字段客观画像（外键连线依据）
field_profile = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv")
fk_fields = [f for f in field_profile if f["field_role"] == "foreign_key"]

# 读取 ODS 表清单
ods_tables = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_ods_inventory.csv")
```
