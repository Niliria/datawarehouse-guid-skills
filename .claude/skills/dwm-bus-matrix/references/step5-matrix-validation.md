# 第五步：矩阵验证与最终交付物发布

## 0. 本步定位

双重职责：
1. **验证**：确认第四步的总线矩阵草稿"可跑通、可解释、可复用"
2. **交付**：将工作底稿合成为可直接指导建设的最终交付物

最终交付物：

| 交付物 | 面向谁 | 作用 |
|--------|--------|------|
| `dwm_bus_matrix`（published） | 业务方 + 技术方 | 企业级建模蓝图 |
| `dwm_dwd_fact_spec` | DWD 开发者 | 字段级事实表建设规格，含 ODS 溯源 |
| `dwm_dim_table_spec` | DIM 开发者 | 字段级维度表建设规格，含 ODS 溯源 |
| `dwm_subject_area_summary` | 管理层 + 业务方 | 主题域全景清单 |

核心原则：**一个业务过程 = 一张 DWD 事实表**。

---

## 1. 输入

| 输入项 | 来源 | 用途 |
|--------|------|------|
| `dwm_bus_matrix`（status=draft） | 第四步 | 待验证的矩阵草稿 |
| `dwm_s4_fact_dim_ref` | 第四步 | 维度引用底稿 → 合成 DWD spec |
| `dwm_s4_fact_metric` | 第四步 | 度量归属底稿 → 合成 DWD spec |
| `dwm_s4_dim_registry` | 第四步 | 一致性维度底稿 → 合成 DIM spec |
| `dwm_s3_table_profile` | 第三步 | 业务过程、粒度声明、表角色 |
| `dwm_s3_subject_area` | 第三步 | 主题域主数据 |
| `dwm_s2_field_tag` | 第二步 | 字段元数据（ODS 溯源） |
| `dwm_s1_ods_inventory` | 第一步 | 同步模式（DWD 表名后缀依据） |

---

## 2. 实施步骤

### 2.1 矩阵验证

1. **逐行验证（业务过程）**：
   - 每个业务过程是否能按关联维度稳定聚合
   - 粒度唯一性验证（ODS 层可直接执行）
2. **逐列验证（一致性维度）**：
   - 每个一致性维度是否可在关联事实中稳定 JOIN
   - JOIN 缺失率 <= 1%
3. **业务语义验证**：
   - 聚合结果是否符合常识与业务口径
4. **记录异常并回溯**：
   - 键质量、口径冲突、缺失维度
5. 产出 `dwm_s5_matrix_check`，验证通过后更新 `dwm_bus_matrix` status 为 published

**粒度唯一性验证 SQL**：

```sql
SELECT
  COUNT(*) AS total_row_cnt,
  COUNT(DISTINCT order_no) AS grain_distinct_cnt
FROM ods_my001_order
WHERE dt = '${check_dt}';
```

检查规则：
- `total_row_cnt = grain_distinct_cnt` → 通过
- 不一致 → 回退第三步修正粒度声明

> **注**：聚合值与源系统的一致性校验（`diff_rate <= 0.1%`）需在 DWD 建成后执行，属于建设阶段验收（见附录 A）。

### 2.2 合成 DWD 事实表建设清单

对每个业务过程（= 一张 DWD 事实表），生成字段级建设规格：

1. **生成 DWD 表名**：`dwd_{subject_area_code}_{bp_standard_name}_{suffix}`（`subject_area_code` 统一转小写）
   - suffix 依据 `dwm_s1_ods_inventory.sync_mode`：`FULL` → `df`，`INCR` → `di`
2. **汇总字段**（按以下顺序）：
   - 粒度键：来自 `dwm_s3_table_profile.grain_keys`
   - 维度外键：来自 `dwm_s4_fact_dim_ref WHERE dimension_type='外键'`
   - 退化维度：来自 `dwm_s4_fact_dim_ref WHERE dimension_type='退化维度'`
   - 低基数离散属性：来自 `dwm_s4_fact_dim_ref WHERE dimension_type='低基数离散属性候选'`
   - 度量字段：来自 `dwm_s4_fact_metric`
   - 业务时间：来自 `dwm_s2_field_tag WHERE core_tag='业务时间'`
3. **标注 ODS 溯源**：每个字段通过 `dwm_s2_field_tag` 关联 `ods_table_name` + `col_name`，并通过 `dwm_s1_field_registry.data_type` 填充 `ods_data_type`
4. **标注维度关联**：外键字段标注关联的 DIM 表（来自 `dwm_s4_dim_registry.dimension_key`）
5. 产出 `dwm_dwd_fact_spec`

### 2.3 合成 DIM 维度表建设清单

对每个一致性维度（= 一张 DIM 表），生成字段级建设规格：

1. **DIM 表名**：直接使用 `dwm_s4_dim_registry.dimension_key`（如 `dim_supplier`）
2. **汇总字段**（按以下顺序）：
   - 粒度键（业务键/代理键）：来自 `dwm_s4_dim_registry.grain_keys`
   - 维度属性：来自 `dwm_s4_dim_registry.dimension_columns`
   - **不包含** SCD 管理字段（`dw_start_date`/`dw_end_date`/`dw_is_current`），这些由 DIM 建设阶段 ETL 自动生成，SCD 策略已在 `dwm_s4_dim_registry` 中声明
3. **标注 ODS 溯源**：通过 `dwm_s2_field_tag WHERE ods_table_name = source_dimension_table` 关联 `ods_table_name` + `col_name`，并通过 `dwm_s1_field_registry.data_type` 填充 `ods_data_type`
4. **标注 SCD 类型**：解析 `dwm_s4_dim_registry.scd_columns`，逐字段标注 `SCD1`/`SCD2`/`SCD3`/`-`
5. 产出 `dwm_dim_table_spec`

### 2.4 合成主题域清单

对每个主题域，汇总统计信息：

1. 基础信息：来自 `dwm_s3_subject_area`
2. 业务过程数：`COUNT(*) FROM dwm_s3_table_profile WHERE subject_area_code=X AND table_role='fact'`
3. DWD 表数 = 业务过程数（一个业务过程 = 一张 DWD 表）
4. 关联 DIM 表数：该域下事实表关联的去重 DIM 表数量
5. 源 ODS 表数：该域下所有 `table_role != 'exclude'` 的 ODS 表数量
6. 列出业务过程名、DWD 表名、DIM 表名
7. 产出 `dwm_subject_area_summary`

### 2.5 建设优先级规划

1. 以业务价值、复用度、实施复杂度评估优先级
2. 标注 `P0` / `P1` / `P2`，给出排序依据
3. 输出阶段计划：先维度后事实、先核心过程后边缘过程
4. 产出 `dwm_s5_priority_roadmap`

---

## 3. 产出物

### 3.1 `dwm_s5_matrix_check`（矩阵验证报告）

一行一条验证项。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| check_id | 检查项编号 | 是 | 自增主键 |
| check_type | 检查类型 | 是 | `join验证` / `粒度唯一性验证` / `口径验证` / `应连未连` |
| business_process | 业务过程（行） | 是 | 来自 `dwm_s3_table_profile.bp_standard_name` |
| dimension_key | 维度键（列） | 条件 | `check_type IN ('join验证','口径验证','应连未连')` 时必填 |
| ref_table | 引用维表名 | 条件 | `check_type=join验证` 时必填 |
| ref_column | 引用字段名 | 条件 | `check_type=join验证` 时必填 |
| issue_desc | 问题描述 | 是 | 简述问题现象 |
| check_sql | 验证 SQL | 条件 | `check_type IN ('join验证','粒度唯一性验证','口径验证')` 时填可执行 SQL |
| check_result | 检查结果 | 是 | `pass` / `fail` / `pending` |
| fail_reason | 失败原因 | 条件 | `check_result=fail` 时必填 |
| risk_level | 风险等级 | 是 | `高` / `中` / `低` |
| handle_decision | 处置结论 | 是 | `修正` / `豁免` / `延期` |
| handle_action | 处置行动 | 条件 | 处置结论为"修正"时必填 |
| handle_who | 责任人 | 是 | 执行人 |
| handle_deadline | 截止时间 | 是 | 处置截止日期 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`check_id`

### 3.2 `dwm_dwd_fact_spec`（DWD 事实表建设清单）

一行一个字段。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| dwd_table_name | DWD 表名 | 是 | `dwd_{subject_area_code}_{bp_standard_name}_{suffix}` |
| subject_area_code | 主题域编码 | 是 | 外键引用 `dwm_s3_subject_area` |
| bp_standard_name | 业务过程标准名 | 是 | 来自 `dwm_s3_table_profile` |
| fact_type | 事实表类型 | 是 | `transaction` / `periodic_snapshot` / `accumulating_snapshot` / `factless` |
| grain_statement | 粒度声明 | 是 | 来自 `dwm_s3_table_profile.grain_statement` |
| dwd_column_name | DWD 字段名 | 是 | DWD 层字段命名 |
| dwd_column_comment | 字段中文说明 | 是 | 来自 `dwm_s2_field_tag.col_comm` 或人工修正 |
| column_role | 字段角色 | 是 | `grain_key` / `fk` / `degenerate_dim` / `low_card_attr` / `measure` / `business_time` |
| ods_table_name | 来源 ODS 表 | 是 | 来自 `dwm_s2_field_tag.ods_table_name` |
| ods_column_name | 来源 ODS 字段 | 是 | 来自 `dwm_s2_field_tag.col_name` |
| ods_data_type | ODS 字段数据类型 | 是 | 来自 `dwm_s1_field_registry.data_type`，如 `varchar(255)` / `int` / `decimal(10,2)` |
| ref_dim_table | 关联 DIM 表 | 条件 | `column_role=fk` 时必填，来自 `dwm_s4_dim_registry.dimension_key` |
| agg_suggest | 聚合建议 | 条件 | `column_role=measure` 时必填 |
| unit | 度量单位 | 条件 | `column_role=measure` 时必填 |
| is_derived | 是否派生 | 条件 | `column_role=measure` 时必填 |
| derived_logic | 派生逻辑 | 条件 | `is_derived=Y` 时必填 |
| sort_order | 字段排序 | 是 | 整数，按 `grain_key→fk→degenerate_dim→low_card_attr→measure→business_time` |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`dwd_table_name + dwd_column_name`

### 3.3 `dwm_dim_table_spec`（DIM 维度表建设清单）

一行一个字段。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| dim_table_name | DIM 表名 | 是 | 来自 `dwm_s4_dim_registry.dimension_key` |
| dimension_name | 维度中文名 | 是 | 来自 `dwm_s4_dim_registry.dimension_name` |
| dim_column_name | DIM 字段名 | 是 | DIM 层字段命名 |
| dim_column_comment | 字段中文说明 | 是 | 来自 `dwm_s2_field_tag.col_comm` 或人工修正 |
| column_role | 字段角色 | 是 | `pk` / `bk` / `attribute` |
| scd_type | SCD 类型 | 条件 | `column_role=attribute` 时必填：`SCD1` / `SCD2` / `SCD3` / `-` |
| ods_table_name | 来源 ODS 表 | 是 | 来自 `dwm_s4_dim_registry.source_dimension_table` |
| ods_column_name | 来源 ODS 字段 | 是 | 来自 `dwm_s2_field_tag.col_name` |
| ods_data_type | ODS 字段数据类型 | 是 | 来自 `dwm_s1_field_registry.data_type`，如 `varchar(255)` / `int` / `decimal(10,2)` |
| sort_order | 字段排序 | 是 | 整数，按 `pk→bk→attribute` |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`dim_table_name + dim_column_name`
>
> SCD 管理字段（`dw_start_date`/`dw_end_date`/`dw_is_current`）不纳入本表。SCD 策略已在 `dwm_s4_dim_registry.scd_strategy` + `scd_columns` 中声明，管理字段由 DIM 建设阶段 ETL 自动生成。

### 3.4 `dwm_subject_area_summary`（主题域清单）

一行一个主题域。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| subject_area_code | 主题域编码 | 是 | 主键，来自 `dwm_s3_subject_area` |
| subject_area_name_cn | 中文名称 | 是 | 来自 `dwm_s3_subject_area` |
| subject_area_name_en | 英文名称 | 是 | 来自 `dwm_s3_subject_area` |
| subject_area_desc | 描述 | 是 | 来自 `dwm_s3_subject_area` |
| bp_count | 业务过程数 | 是 | 该域下 `table_role=fact` 的表数量 |
| dwd_table_count | DWD 事实表数 | 是 | = `bp_count` |
| dim_table_count | 关联 DIM 维度表数 | 是 | 该域下事实表关联的去重 DIM 表数量 |
| ods_table_count | 源 ODS 表数 | 是 | 该域下 `table_role != 'exclude'` 的 ODS 表数量 |
| bp_list | 业务过程列表 | 是 | 逗号分隔的 `bp_standard_name` |
| dwd_table_list | DWD 表名列表 | 是 | 逗号分隔的 `dwd_table_name` |
| dim_table_list | 关联 DIM 表列表 | 是 | 逗号分隔的 `dim_table_name` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code`

### 3.5 `dwm_s5_priority_roadmap`（优先级路线图）

一行一个建模任务。按主题域分组输出发布清单。产出格式：数据库表 / CSV。

> **性质说明**：本表为建设规划输出，非建模元数据，生命周期与项目节奏对齐，可按迭代周期更新。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| subject_area_code | 主题域编码 | 是 | 外键引用 `dwm_s3_subject_area` |
| object_type | 对象类型 | 是 | `dimension` / `fact` |
| object_name | 对象名称 | 是 | 维表名或事实表名 |
| bp_standard_name | 业务过程标准名 | 条件 | `object_type=fact` 时必填 |
| priority | 优先级 | 是 | `P0` / `P1` / `P2` |
| priority_basis | 优先级依据 | 是 | 业务价值 / 复用度 / 实施复杂度 |
| phase | 建设阶段 | 是 | `Phase1` / `Phase2` / `Phase3` |
| dependent_objects | 依赖对象 | 否 | 依赖的其他维表/事实表 |
| remarks | 备注 | 否 | 如复杂属性拆解依赖 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code + object_type + object_name`

### 3.6 总线矩阵发布

验证通过后，将 `dwm_bus_matrix` 的 `status` 从 `draft` 更新为 `published`，`version` 递增（如 `v1.0`）。矩阵结构详见 step4 §3.4。

---

## 4. 验收标准

1. **JOIN 验证**：核心维度与事实的 JOIN 缺失率 <= 1%
2. **粒度唯一性**：每个业务过程粒度键在 ODS 层 100% 通过
3. **口径验证**：一致性维度在不同事实中口径一致
4. **异常闭环**：`dwm_s5_matrix_check` 中所有 `fail` 项均有 `handle_decision`
5. **DWD spec 完整性**：每张 DWD 表的字段数 = 粒度键数 + 维度外键数 + 退化维度数 + 度量数 + 业务时间数
6. **DIM spec 完整性**：每张 DIM 表的字段数 = 粒度键数 + 维度属性数（不含 SCD 管理字段，SCD 策略由 `dwm_s4_dim_registry` 声明）
7. **主题域汇总一致性**：`subject_area_summary.bp_count` 与 `table_profile` 中 fact 行数一致
8. **可追溯**：所有 DWD/DIM 字段的 `ods_table_name`、`ods_column_name`、`ods_data_type` 非空

---

## 5. 与建设阶段衔接

- `dwm_dwd_fact_spec` → DWD 开发直接建表，字段定义和 ODS 溯源一步到位
- `dwm_dim_table_spec` → DIM 开发直接建表，SCD 策略已明确
- `dwm_bus_matrix`（published）→ 企业级建模权威蓝图
- `dwm_subject_area_summary` → 管理层了解全景，指导资源分配
- `dwm_s5_priority_roadmap` → 以 `P0` 过程优先进入 DIM 与 DWD 建设
- `dwm_s5_matrix_check` 中的 `豁免` 项须在建设阶段做特殊处理（如 NULL 填充策略）
- 复杂属性拆解决策根据 `dwm_s2_field_tag` 中的 `complex_type` 标注执行

---

## 附录 A：建设阶段反馈机制

> 以下内容在建设阶段执行，非第五步范围。

五步流程在矩阵发布后进入建设阶段。建设中发现的数据问题通过此机制反馈回矩阵，形成闭环。

### A.1 建设阶段验证（DWD 建成后执行）

| 验证项 | 验证时机 | 检查规则 | 失败处理 |
|--------|---------|---------|---------| 
| 粒度可聚合性 | DWD 建成后 | 聚合值与源系统差异率 <= 0.1% | 回退第三步或第四步 |
| 维度 JOIN 一致性 | DIM + DWD 联调时 | 生产 JOIN miss_rate <= 1% | 回退第四步 |
| 复杂属性拆解验证 | DWD 扁平化完成后 | 拆解覆盖率 + 数据正确性 | 修正拆解策略 |

### A.2 反馈触发与回退路径

| 触发条件 | 回退目标 | 处理方式 |
|---------|---------|---------|
| DWD 聚合差异 > 0.1% | 第四步 `dwm_s4_fact_metric` | 检查度量归属或事实表类型 |
| 生产 JOIN miss_rate 远高于采样 | 第二步 `dwm_s2_field_tag` | 数据质量问题或 FK 关系误判 |
| 新业务上线产生新业务过程 | 第三步 `dwm_s3_table_profile` | 走第三~五步增量流程 |
| 口径争议升级 | 第四步 `dwm_s4_dim_registry` | 重新做一致性校验 |

### A.3 变更管理

1. 所有建设阶段反馈记录到 `dwm_s5_matrix_check`（`check_type` 扩展为 `建设反馈` / `回退变更`）
2. 矩阵版本化：每次修正后更新 `dwm_bus_matrix` 的 `version`
3. 修正后的产出物须重新通过对应步骤的验收标准
