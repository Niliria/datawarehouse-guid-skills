# ⑤ 组装总线矩阵：验证 + 交付物合成 + 优先级规划

双重职责：验证第四步总线矩阵草稿"可跑通、可解释、可复用"，并将工作底稿合成为可直接指导建设的最终交付物。

**核心原则**：一个业务过程 = 一张 DWD 事实表。

---

## 1. 输入

| 输入项 | 来源 Skill | 用途 |
|--------|-----------|------|
| `dwm_bp_business_process` | ② | 业务过程、粒度声明、事实表类型 |
| `dwm_bp_metric` | ② | 度量归属底稿 → 合成 DWD spec |
| `dwm_bp_subject_area` | ② | 主题域主数据 |
| `dwm_dim_registry` | ③ | 一致性维度注册表 → 总线矩阵列头 + DIM spec |
| `dwm_inv_field_profile` | ① | 字段元数据（FK 关系推导维度引用、ODS 溯源、退化维度/低基数属性推导） |
| `dwm_inv_field_registry` | ① | 字段类型信息（`data_type`，填充 `ods_data_type`） |
| `dwm_inv_ods_inventory` | ① | 同步模式（DWD 表名后缀依据） |

---

## 2. 实施步骤

### 2.1 矩阵验证

> 如需编写批量验证 SQL 脚本，use context7 获取对应 SQL 方言（HiveQL / SparkSQL）的最新文档。

**逐行验证（业务过程）**：
- 每个业务过程能否按关联维度稳定聚合
- 粒度唯一性验证（ODS 层直接执行）

**粒度唯一性验证 SQL**：
```sql
SELECT
  COUNT(*) AS total_row_cnt,
  COUNT(DISTINCT ${grain_key_cols}) AS grain_distinct_cnt
FROM ${ods_table_name}
WHERE dt = '${check_dt}';
-- total_row_cnt = grain_distinct_cnt → 通过
-- 不一致 → 回退 ② 修正粒度声明
```

**逐列验证（一致性维度）**：
- 每个一致性维度能否在关联事实中稳定 JOIN
- JOIN 缺失率 ≤ 1%

**JOIN 缺失率验证 SQL**：
```sql
SELECT
  COUNT(1) AS ref_cnt,
  SUM(CASE WHEN b.${ref_col} IS NULL THEN 1 ELSE 0 END) AS miss_cnt,
  ROUND(SUM(CASE WHEN b.${ref_col} IS NULL THEN 1 ELSE 0 END) / COUNT(1), 4) AS miss_rate
FROM ${fact_ods_table} a
LEFT JOIN ${dim_ods_table} b ON a.${fk_col} = b.${ref_col}
WHERE a.${fk_col} IS NOT NULL
  AND a.dt = '${check_dt}';
-- miss_rate ≤ 0.01 → 通过
```

**业务语义验证**：聚合结果是否符合常识与业务口径。

验证结果写入 `dwm_matrix_check`，通过后更新 `dwm_bus_matrix.xlsx` status 为 published。

> **注**：聚合值与源系统的一致性校验（`diff_rate ≤ 0.1%`）需在 DWD 建成后执行，属于建设阶段验收（见 §6 附录 A）。

### 2.2 合成 DWD 事实表建设清单

对每个业务过程（= 一张 DWD 事实表），生成字段级建设规格：

1. **生成 DWD 表名**：`dwd_{subject_area_code_lowercase}_{bp_standard_name}_{suffix}`
   - suffix 依据 `dwm_inv_ods_inventory.sync_mode`：`FULL` → `df`，`INCR` → `di`
2. **汇总字段**（按以下固定顺序，对应 `sort_order`）：
   - 粒度键（`grain_key`）：来自 `dwm_bp_business_process.粒度键`
   - 维度外键（`fk`）：来自 `dwm_inv_field_profile WHERE field_role='foreign_key'`，通过 `ref_table` 映射到 `dwm_dim_registry`
   - 退化维度（`degenerate_dim`）：来自 `dwm_inv_field_profile WHERE field_role='primary_key' AND is_surrogate='N'`（事实表中的天然业务键）
   - 低基数离散属性（`low_card_attr`）：来自 `dwm_inv_field_profile WHERE field_role='low_cardinality'`（事实表中的低基数字段）
   - 度量字段（`measure`）：来自 `dwm_bp_metric`
   - 业务时间（`business_time`）：来自 `dwm_inv_field_profile WHERE field_role='business_time'`
3. **标注 ODS 溯源**：每个字段通过 `dwm_inv_field_profile` 关联 `ods_table_name` + `col_name`，通过 `dwm_inv_field_registry.data_type` 填充 `ods_data_type`
4. **标注维度关联**：外键字段标注关联的 DIM 表（来自 `dwm_dim_registry.dimension_key`）

### 2.3 合成 DIM 维度表建设清单

对每个一致性维度（= 一张 DIM 表），生成字段级建设规格：

1. **DIM 表名**：直接使用 `dwm_dim_registry.dimension_key`（如 `dim_user`）
2. **汇总字段**（按以下固定顺序）：
   - 粒度键（`pk`/`bk`）：来自 `dwm_dim_registry.grain_keys`
   - 维度属性（`attribute`）：来自 `dwm_dim_registry.dimension_columns`
   - **不包含** SCD 管理字段（`dw_start_date`/`dw_end_date`/`dw_is_current`），这些由 DIM 建设阶段 ETL 自动生成
3. **标注 ODS 溯源**：通过 `dwm_inv_field_profile WHERE ods_table_name = source_dimension_table` 关联
4. **标注 SCD 类型**：解析 `dwm_dim_registry.scd_columns`，逐字段标注 `SCD1`/`SCD2`/`SCD3`/`-`

### 2.4 合成主题域清单

对每个主题域，汇总统计信息：

1. 基础信息：来自 `dwm_bp_subject_area`
2. 业务过程数：`COUNT(*) FROM dwm_bp_business_process WHERE 主题域编码=X`
3. DWD 表数 = 业务过程数
4. 关联 DIM 表数：该域下事实表关联的去重 DIM 表数量
5. 源 ODS 表数：该域下业务过程涉及的 ODS 表数量

### 2.5 生成总线矩阵 Excel

```bash
python .claude/skills/dwm-5-bus-matrix/scripts/write_bus_matrix.py \
  --business-process output/dwm-bus-matrix/business-process/dwm_bp_business_process.csv \
  --subject-area  output/dwm-bus-matrix/business-process/dwm_bp_subject_area.csv \
  --dim-registry  output/dwm-bus-matrix/dimension/dwm_dim_registry.csv \
  --field-profile output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv \
  --output        output/dwm-bus-matrix/dwm_bus_matrix.xlsx \
  --version v1.0
```

> 如需安装依赖或修改脚本，use context7 获取 openpyxl 最新文档（`pip install openpyxl`）。

### 2.6 建设优先级规划

1. 以业务价值、复用度、实施复杂度评估优先级
2. 标注 `P0` / `P1` / `P2`，给出排序依据
3. 建设顺序：先维度后事实，先核心过程后边缘过程

---

## 3. 产出物

### 3.1 `dwm_matrix_check`（矩阵验证报告）

一行一条验证项。产出格式：CSV，路径 `output/dwm-bus-matrix/assembly/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| check_id | 检查项编号 | 是 | 自增主键 |
| check_type | 检查类型 | 是 | `join验证` / `粒度唯一性验证` / `口径验证` / `应连未连` |
| business_process | 业务过程（行） | 是 | 来自 `dwm_bp_business_process.业务过程英文名称` |
| dimension_key | 维度键（列） | 条件 | `check_type IN ('join验证','口径验证','应连未连')` 时必填 |
| ref_table | 引用维表名 | 条件 | `check_type='join验证'` 时必填 |
| ref_column | 引用字段名 | 条件 | `check_type='join验证'` 时必填 |
| issue_desc | 问题描述 | 是 | 简述问题现象 |
| check_sql | 验证 SQL | 条件 | `check_type IN ('join验证','粒度唯一性验证','口径验证')` 时填可执行 SQL |
| check_result | 检查结果 | 是 | `pass` / `fail` / `pending` |
| fail_reason | 失败原因 | 条件 | `check_result='fail'` 时必填 |
| risk_level | 风险等级 | 是 | `高` / `中` / `低` |
| handle_decision | 处置结论 | 是 | `修正` / `豁免` / `延期` |
| handle_action | 处置行动 | 条件 | `handle_decision='修正'` 时必填 |
| handle_who | 责任人 | 是 | 执行人 |
| handle_deadline | 截止时间 | 是 | 处置截止日期 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`check_id`

### 3.2 `dwm_dwd_fact_spec`（DWD 事实表建设清单）★ 最终交付物

一行一个字段。产出格式：CSV，路径 `output/dwm-bus-matrix/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| dwd_table_name | DWD 表名 | 是 | `dwd_{subject_area_code}_{bp_standard_name}_{df/di}` |
| subject_area_code | 主题域编码 | 是 | 关联 `dwm_bp_subject_area` |
| bp_standard_name | 业务过程标准名 | 是 | 来自 `dwm_bp_business_process` |
| fact_type | 事实表类型 | 是 | `transaction` / `periodic_snapshot` / `accumulating_snapshot` / `factless` |
| grain_statement | 粒度声明 | 是 | 来自 `dwm_bp_business_process.粒度声明` |
| dwd_column_name | DWD 字段名 | 是 | DWD 层字段命名 |
| dwd_column_comment | 字段中文说明 | 是 | 来自 `dwm_inv_field_profile.col_comment` 或人工修正 |
| column_role | 字段角色 | 是 | `grain_key` / `fk` / `degenerate_dim` / `low_card_attr` / `measure` / `business_time` |
| ods_table_name | 来源 ODS 表 | 是 | 来自 `dwm_inv_field_profile.ods_table_name` |
| ods_column_name | 来源 ODS 字段 | 是 | 来自 `dwm_inv_field_profile.col_name` |
| ods_data_type | ODS 字段数据类型 | 是 | 来自 `dwm_inv_field_registry.data_type`，如 `varchar(255)` / `decimal(10,2)` |
| ref_dim_table | 关联 DIM 表 | 条件 | `column_role='fk'` 时必填，来自 `dwm_dim_registry.dimension_key` |
| agg_suggest | 聚合建议 | 条件 | `column_role='measure'` 时必填 |
| unit | 度量单位 | 条件 | `column_role='measure'` 时必填 |
| is_derived | 是否派生 | 条件 | `column_role='measure'` 时必填 |
| derived_logic | 派生逻辑 | 条件 | `is_derived='Y'` 时必填 |
| sort_order | 字段排序 | 是 | 整数，按 `grain_key→fk→degenerate_dim→low_card_attr→measure→business_time` |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`dwd_table_name + dwd_column_name`

### 3.3 `dwm_dim_table_spec`（DIM 维度表建设清单）★ 最终交付物

一行一个字段。产出格式：CSV，路径 `output/dwm-bus-matrix/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| dim_table_name | DIM 表名 | 是 | 来自 `dwm_dim_registry.dimension_key` |
| dimension_name | 维度中文名 | 是 | 来自 `dwm_dim_registry.dimension_name` |
| dim_column_name | DIM 字段名 | 是 | DIM 层字段命名 |
| dim_column_comment | 字段中文说明 | 是 | 来自 `dwm_inv_field_profile.col_comment` 或人工修正 |
| column_role | 字段角色 | 是 | `pk`（代理键）/ `bk`（业务键）/ `attribute` |
| scd_type | SCD 类型 | 条件 | `column_role='attribute'` 时必填：`SCD1` / `SCD2` / `SCD3` / `-` |
| ods_table_name | 来源 ODS 表 | 是 | 来自 `dwm_dim_registry.source_dimension_table` |
| ods_column_name | 来源 ODS 字段 | 是 | 来自 `dwm_inv_field_profile.col_name` |
| ods_data_type | ODS 字段数据类型 | 是 | 来自 `dwm_inv_field_registry.data_type` |
| sort_order | 字段排序 | 是 | 整数，按 `pk→bk→attribute` |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`dim_table_name + dim_column_name`
>
> SCD 管理字段（`dw_start_date`/`dw_end_date`/`dw_is_current`）**不纳入本表**。SCD 策略已在 `dwm_dim_registry.scd_strategy` + `scd_columns` 中声明，管理字段由 DIM 建设阶段 ETL 自动生成。

### 3.4 `dwm_subject_area_summary`（主题域清单）★ 最终交付物

一行一个主题域。产出格式：CSV，路径 `output/dwm-bus-matrix/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| subject_area_code | 主题域编码 | 是 | 主键，来自 `dwm_bp_subject_area` |
| subject_area_name_cn | 中文名称 | 是 | 来自 `dwm_bp_subject_area` |
| subject_area_name_en | 英文名称 | 是 | 来自 `dwm_bp_subject_area` |
| subject_area_desc | 描述 | 是 | 来自 `dwm_bp_subject_area` |
| bp_count | 业务过程数 | 是 | 该域下业务过程数量 |
| dwd_table_count | DWD 事实表数 | 是 | = `bp_count` |
| dim_table_count | 关联 DIM 维度表数 | 是 | 该域下事实表关联的去重 DIM 表数量 |
| ods_table_count | 源 ODS 表数 | 是 | 该域下业务过程涉及的 ODS 表数量 |
| bp_list | 业务过程列表 | 是 | 逗号分隔的 `bp_standard_name` |
| dwd_table_list | DWD 表名列表 | 是 | 逗号分隔的 `dwd_table_name` |
| dim_table_list | 关联 DIM 表列表 | 是 | 逗号分隔的 `dim_table_name` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code`

### 3.5 `dwm_priority_roadmap`（优先级路线图）

一行一个建模任务。产出格式：CSV，路径 `output/dwm-bus-matrix/assembly/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| subject_area_code | 主题域编码 | 是 | 关联 `dwm_bp_subject_area` |
| object_type | 对象类型 | 是 | `dimension` / `fact` |
| object_name | 对象名称 | 是 | 维表名（`dim_xxx`）或事实表名（`dwd_xxx`） |
| bp_standard_name | 业务过程标准名 | 条件 | `object_type='fact'` 时必填 |
| priority | 优先级 | 是 | `P0` / `P1` / `P2` |
| priority_basis | 优先级依据 | 是 | 业务价值 / 复用度 / 实施复杂度 |
| phase | 建设阶段 | 是 | `Phase1` / `Phase2` / `Phase3` |
| dependent_objects | 依赖对象 | 否 | 依赖的其他维表/事实表，逗号分隔 |
| remarks | 备注 | 否 | 如复杂属性拆解依赖 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code + object_type + object_name`

### 3.6 `dwm_bus_matrix.xlsx`（总线矩阵）★ 最终交付物

Excel 格式，路径 `output/dwm-bus-matrix/`。

验证通过后，`status` 从 `draft` 更新为 `published`，`version` 递增（如 `v1.0`）。

Excel 结构：
- Sheet 名：`总线矩阵 v{version}`
- A 列：主题域（`主题域名称(编码)`，每行填充，不合并）
- B 列：业务过程（中文名，`business_process`）
- C 列：业务过程代码（英文，`bp_standard_name`）
- D 列：粒度声明（`grain_statement`）
- E 列：事实表类型（`fact_type`）
- F 列起：每列一个一致性维度（列头 = `dimension_name`）
- 单元格：`✓` / `-` / 空
- 末行：元数据（version / status / updated_by / updated_at）

---

## 4. 验收标准

1. **JOIN 验证**：核心维度与事实的 JOIN 缺失率 ≤ 1%
2. **粒度唯一性**：每个业务过程粒度键在 ODS 层 100% 通过
3. **口径验证**：一致性维度在不同事实中口径一致
4. **异常闭环**：`dwm_matrix_check` 中所有 `fail` 项均有 `handle_decision`
5. **DWD spec 完整性**：每张 DWD 表字段数 = 粒度键数 + 维度外键数 + 退化维度数 + 度量数 + 业务时间数
6. **DIM spec 完整性**：每张 DIM 表字段数 = 粒度键数 + 维度属性数（不含 SCD 管理字段）
7. **主题域汇总一致性**：`dwm_subject_area_summary.bp_count` 与 `dwm_bp_business_process` 中行数一致
8. **可追溯**：所有 DWD/DIM 字段的 `ods_table_name`、`ods_column_name`、`ods_data_type` 非空

---

## 5. 与建设阶段衔接

| 交付物 | 消费方 | 用途 |
|--------|--------|------|
| `dwm_dwd_fact_spec` | spec-to-dwd-dim-job Skill | 生成 DWD DDL + INSERT OVERWRITE SQL |
| `dwm_dim_table_spec` | spec-to-dwd-dim-job Skill | 生成 DIM DDL + INSERT OVERWRITE SQL |
| `dwm_bus_matrix.xlsx`（published） | 业务方 + 技术负责人 | 企业级建模权威蓝图 |
| `dwm_subject_area_summary` | 管理层 | 全景数仓建设清单 |
| `dwm_priority_roadmap` | 项目负责人 | P0 过程优先进入 DIM 与 DWD 建设 |

---

## 6. 附录 A：建设阶段反馈机制

> 以下内容在建设阶段执行，非本 Skill 范围。

### A.1 建设阶段验证（DWD 建成后执行）

| 验证项 | 验证时机 | 检查规则 | 失败处理 |
|--------|---------|---------|---------|
| 粒度可聚合性 | DWD 建成后 | 聚合值与源系统差异率 ≤ 0.1% | 回退 ②③ |
| 维度 JOIN 一致性 | DIM + DWD 联调时 | 生产 JOIN miss_rate ≤ 1% | 回退 ③ |
| 复杂属性拆解验证 | DWD 扁平化完成后 | 拆解覆盖率 + 数据正确性 | 修正拆解策略 |

### A.2 反馈触发与回退路径

| 触发条件 | 回退目标 | 处理方式 |
|---------|---------|---------|
| DWD 聚合差异 > 0.1% | ② `dwm_bp_metric` | 检查度量归属或事实表类型 |
| 生产 JOIN miss_rate 远高于采样 | ① `dwm_inv_field_profile` | 数据质量问题或 FK 关系误判 |
| 新业务上线产生新业务过程 | ② `dwm_bp_business_process` | 走 ②~⑤ 增量流程 |
| 口径争议升级 | ③ `dwm_dim_registry` | 重新做一致性校验 |

### A.3 变更管理

1. 所有建设阶段反馈记录到 `dwm_matrix_check`（`check_type` 扩展为 `建设反馈` / `回退变更`）
2. 矩阵版本化：每次修正后更新 `dwm_bus_matrix.xlsx` 的 `version`
3. 修正后的产出物须重新通过对应步骤的验收标准

---

## 7. 代码规范

### CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

### 读取上游产出

```python
# 读取所有上游产出
table_profile = read_csv("output/dwm-bus-matrix/business-process/dwm_bp_business_process.csv")  # 含事实表类型
metrics      = read_csv("output/dwm-bus-matrix/business-process/dwm_bp_metric.csv")
subject_area  = read_csv("output/dwm-bus-matrix/business-process/dwm_bp_subject_area.csv")
dim_registry = read_csv("output/dwm-bus-matrix/dimension/dwm_dim_registry.csv")
ods_inventory = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_ods_inventory.csv")
field_profile = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv")
field_registry = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_registry.csv")
```

### 合成脚本结构（大数据量时）

> 需要编写合成脚本时，use context7 获取相关 Python 库（pandas 等）的最新文档。

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv

# 读取上游 → 合成逻辑 → 写入最终交付物
# 合成 DWD spec
dwd_spec_rows = []
# ... 合成逻辑
write_csv("output/dwm-bus-matrix/dwm_dwd_fact_spec.csv", dwd_spec_rows)

# 合成 DIM spec
dim_spec_rows = []
# ... 合成逻辑
write_csv("output/dwm-bus-matrix/dwm_dim_table_spec.csv", dim_spec_rows)
```
