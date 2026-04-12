# 第五步：矩阵验证与优先级发布

验证矩阵"可跑通、可解释、可复用"，并将建模蓝图转成可执行路线图。

---

## 1. 输入

| 输入项 | 来源 | 用途 |
|--------|------|------|
| `dwm_s3_table_profile WHERE table_role='fact'` | 第三步 | 业务过程清单与粒度声明 |
| `dwm_s3_table_profile WHERE table_role='dimension'` | 第三步 | 维度候选表与粒度键 |
| `dwm_s3_subject_area` | 第三步 | 主题域主数据，路线图按主题域分组 |
| `dwm_s4_bus_matrix`（status=draft） | 第四步 | 待验证的维度-事实关联矩阵 |
| `dwm_s4_fact_dim_ref` | 第四步 | 维度引用证据链 |
| `dwm_s4_fact_metric` | 第四步 | 度量归属与聚合建议 |
| `dwm_s4_dim_registry` | 第四步 | 一致性维度注册表 |
| `dwm_s2_field_tag WHERE core_tag=度量` | 第二步 | 度量字段明细 |

---

## 2. 实施步骤

### 2.1 矩阵验证

1. **逐行验证（业务过程维度）**：
   - 每个业务过程是否能按关联维度稳定聚合
   - 粒度唯一性验证（ODS 层可直接执行）
2. **逐列验证（一致性维度维度）**：
   - 每个一致性维度是否可在关联事实中稳定 JOIN
   - JOIN 缺失率 <= 1%
3. **业务语义验证**：
   - 聚合结果是否符合常识与业务口径
4. **记录异常并回溯**：
   - 键质量、口径冲突、缺失维度
5. 产出 `dwm_s5_matrix_check`，验证通过后更新 `dwm_s4_bus_matrix` status 为 published

**粒度唯一性验证 SQL**：

```sql
-- 验证事实表粒度唯一性（ODS 层）
SELECT
  COUNT(*) AS total_row_cnt,
  COUNT(DISTINCT order_no) AS grain_distinct_cnt
FROM ods_my001_order
WHERE dt = '${check_dt}';
```

检查规则：
- `total_row_cnt = grain_distinct_cnt` → 通过
- 不一致 → 回退第三步修正粒度声明

> **注**：聚合值与源系统的一致性校验（`diff_rate <= 0.1%`）需在 DWD 建成后执行，属于建设阶段验收（见 §4）。

### 2.2 优先级标注与发布

1. 以业务价值、复用度、实施复杂度评估优先级
2. 标注 `P0` / `P1` / `P2`，给出排序依据
3. 输出阶段计划：先维度后事实、先核心过程后边缘过程
4. 形成发布版总线矩阵与建设任务清单

---

## 3. 产出物

### 3.1 `dwm_s5_matrix_check`（矩阵验证报告表）

一行一条问题或检查项。产出格式：数据库表 / CSV。

> **此表在项目初始化时预创建**，贯穿全流程使用（回退变更、建设反馈均写入此表）。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| check_id | 检查项编号 | 是 | 自增主键 |
| check_type | 检查类型 | 是 | `join验证` / `粒度唯一性验证` / `口径验证` / `缺失维度` / `应连未连` / `建设反馈` / `回退变更` |
| business_process | 业务过程（行） | 是 | 来自 `dwm_s3_table_profile.bp_standard_name` |
| dimension_key | 维度键（列） | 条件 | `check_type IN ('join验证','缺失维度','应连未连','口径验证')` 时必填，其余留空 |
| ref_table | 引用维表名 | 条件 | `check_type=join验证` 时必填 |
| ref_column | 引用字段名 | 条件 | `check_type=join验证` 时必填 |
| issue_desc | 问题描述 | 是 | 简述问题现象 |
| check_sql | 验证 SQL / 变更描述 | 条件 | `check_type IN ('join验证','粒度唯一性验证','口径验证')` 时填可执行 SQL；其余填变更描述或验证方法 |
| check_result | 检查结果 | 是 | `pass` / `fail` / `pending` |
| fail_reason | 失败原因 | 条件 | `check_result=fail` 时必填 |
| risk_level | 风险等级 | 是 | `高` / `中` / `低` |
| handle_decision | 处置结论 | 是 | `修正` / `豁免` / `延期` |
| handle_action | 处置行动 | 条件 | 处置结论为"修正"时必填 |
| handle_who | 责任人 | 是 | 执行人 |
| handle_deadline | 截止时间 | 是 | 处置截止日期 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`check_id`

### 3.2 `dwm_s5_priority_roadmap`（优先级路线图）

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

### 3.3 总线矩阵发布

验证通过后，将 `dwm_s4_bus_matrix` 的 `status` 从 `draft` 更新为 `published`，`version` 递增（如 `v1.0`）。矩阵全生命周期由 `dwm_s4_bus_matrix` 统一管理，矩阵结构详见 step4 §3.4。

---

## 4. 建设反馈机制

五步流程在矩阵发布后进入建设阶段。建设中发现的数据问题通过此机制反馈回矩阵，形成闭环。

### 4.1 建设阶段验证（DWD 建成后执行）

| 验证项 | 验证时机 | 检查规则 | 失败处理 |
|--------|---------|---------|---------| 
| 粒度可聚合性 | DWD 建成后 | 聚合值与源系统差异率 <= 0.1% | 回退第三步或第四步 |
| 维度 JOIN 一致性 | DIM + DWD 联调时 | 生产 JOIN miss_rate <= 1% | 回退第四步 |
| 复杂属性拆解验证 | DWD 扁平化完成后 | 拆解覆盖率 + 数据正确性 | 修正拆解策略 |

### 4.2 反馈触发与回退路径

| 触发条件 | 回退目标 | 处理方式 |
|---------|---------|---------|
| DWD 聚合差异 > 0.1% | 第四步 `dwm_s4_fact_metric` | 检查度量归属或事实表类型 |
| 生产 JOIN miss_rate 远高于采样 | 第二步 `dwm_s2_field_tag` | 数据质量问题或 FK 关系误判 |
| 新业务上线产生新业务过程 | 第三步 `dwm_s3_table_profile` | 走第三~五步增量流程 |
| 口径争议升级 | 第四步 `dwm_s4_dim_registry` | 重新做一致性校验 |

### 4.3 变更管理

1. 所有建设阶段反馈记录到 `dwm_s5_matrix_check`（`check_type=建设反馈`）
2. 矩阵版本化：每次修正后更新 `dwm_s4_bus_matrix` 的 `version`
3. 修正后的产出物须重新通过对应步骤的验收标准

---

## 5. 验收标准

1. **JOIN 验证**：核心维度与事实的 JOIN 缺失率 <= 1%
2. **粒度唯一性**：每个业务过程粒度键在 ODS 层 100% 通过
3. **口径验证**：一致性维度在不同事实中口径一致
4. **异常闭环**：`dwm_s5_matrix_check` 中所有 `fail` 项均有 `handle_decision`
5. **优先级合理**：`P0` 覆盖核心业务过程与高复用维度，业务方确认
6. **可实施**：每个任务有明确输入、产出与完成标准
7. **可追溯**：所有决策有文档依据，与第二~四步输出可追溯

---

## 6. 与建设阶段衔接

- 以 `P0` 过程优先进入 DIM 与 DWD 建设，再逐步扩展 DWS/ADS
- `dwm_s4_bus_matrix`（status=published）作为 DIM/DWD 建模的权威输入
- `dwm_s5_matrix_check` 中的 `豁免` 项须在建设阶段做特殊处理（如 NULL 填充策略）
- 建设阶段问题通过 §4 反馈机制回写矩阵
- 复杂属性拆解决策根据 `dwm_s2_field_tag` 中的 `complex_type` 标注执行
