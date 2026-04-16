# 第四步：事实与维度确定 + 总线矩阵草稿

## 0. 本步定位

完成 Kimball 四步法的后两步——先确定事实（度量），再确定维度，最后填充总线矩阵草稿。

**为什么先事实后维度？** 事实表类型决定度量的可加性校验规则（事务表度量通常可加，周期快照表度量通常半可加）。不先定类型，度量归属无法校验。

本步产出 4 张**工作底稿**，第五步将其合成为最终交付物（DWD 事实表清单、DIM 维度表清单、总线矩阵发布版、主题域清单）。

| 工作底稿 | 回答什么问题 | 下游消费 |
|----------|------------|---------|
| `dwm_s4_fact_metric` | 每张事实表有哪些度量、怎么聚合？ | → S5 合成 DWD 事实表清单 |
| `dwm_s4_fact_dim_ref` | 每张事实表关联哪些维度？ | → S5 合成 DWD 事实表清单 + 总线矩阵 |
| `dwm_s4_dim_registry` | 哪些维度跨事实表共享、需建 DIM 表？ | → S5 合成 DIM 维度表清单 + 总线矩阵 |
| `dwm_bus_matrix` | 业务过程 × 维度的全景关联 | → S5 验证后发布 |

---

## 1. 输入

| 输入项 | 来源 | 用途 |
|--------|------|------|
| `dwm_s3_table_profile WHERE table_role='fact'` | 第三步 | 业务过程清单与粒度声明 |
| `dwm_s3_table_profile WHERE table_role='dimension'` | 第三步 | 维度候选表与粒度键 |
| `dwm_s2_field_tag WHERE core_tag='外键'` | 第二步 | 表关系证据链（含 `join_miss_rate`） |
| `dwm_s3_subject_area` | 第三步 | 主题域定义，矩阵行分组依据 |
| `dwm_s2_field_tag`（全量） | 第二步 | 字段标签与度量聚合建议 |

---

## 2. 实施步骤

### 2.1 确定事实表类型

对每个业务过程确认事实表类型：

| 类型 | fact_type 编码 | 判定依据 | 典型场景 |
|------|---------------|---------|---------|
| 事务事实表 | `transaction` | 一行一笔业务事件，不可变 | 下单、支付、退款 |
| 周期快照事实表 | `periodic_snapshot` | 按固定周期截面记录状态 | 日库存、月账户余额 |
| 累积快照事实表 | `accumulating_snapshot` | 一行跟踪业务全生命周期，多个里程碑时间 | 订单履约 |

判定规则：
1. 有明确业务事件时间 + 事件后行不变 → 事务事实表
2. 无明确事件、按周期截面 + 半可加度量 → 周期快照事实表
3. 一行有多个里程碑时间、行随流程推进更新 → 累积快照事实表
4. 无度量但有业务行为记录 → 无事实事实表（`factless`）

将 `fact_type`、`fact_type_evidence` 回写到 `dwm_s3_table_profile`：

```sql
UPDATE dwm_s3_table_profile
SET fact_type = 'transaction',
    fact_type_evidence = '有订单时间+金额，一行一笔订单'
WHERE ods_table_name = 'my001_order';
```

### 2.2 确定度量

1. 将 `dwm_s2_field_tag WHERE core_tag IN ('可加度量','半可加度量','不可加度量')` 逐个归属到对应事实表
2. 确认每个度量的 `agg_suggest` 与事实表类型匹配：

| 事实表类型 | 度量特征 |
|-----------|---------|
| `transaction` | 度量通常可加（sum） |
| `periodic_snapshot` | 度量通常半可加（不可跨时间 sum） |
| `accumulating_snapshot` | 里程碑间时间差、状态标志为典型度量 |

3. 识别派生事实（如 `利润 = 收入 - 成本`），标注计算逻辑，决定存储还是运行时计算
4. 产出 `dwm_s4_fact_metric`

### 2.3 提取维度引用

1. 硬门禁：`core_tag IN ('技术属性','技术时间')` 全部剔除，不得进入维度候选池
2. 对每个业务过程从 `dwm_s2_field_tag` 提取 `core_tag='外键'` 字段列表，通过 `ref_table`/`ref_column` 关联到维度候选表
3. 提取同表内 `core_tag='退化维度'` 字段
4. 提取同表内 `core_tag='低基数离散属性候选'` 字段
5. 补充"是否必选维度"与"缺失容忍策略"（如匿名用户）
6. 产出 `dwm_s4_fact_dim_ref`

### 2.4 收敛一致性维度

1. 汇总所有业务过程外键并去重，得到一致性维度候选列表
2. 为每个维度键确定唯一维表来源（从 `dwm_s3_table_profile WHERE table_role='dimension'`）
3. 做一致性检查：命名、口径、编码、值域、JOIN 命中率
4. 仅注册需建 DIM 表的一致性维度（退化维度与低基数离散属性候选已通过 `dwm_s4_fact_dim_ref.dimension_type` 管理，不纳入此表）
5. **SCD 策略确认**：对每个一致性维度中标注了 `ext_tags LIKE '%SCD属性%'` 的字段，正式决策：
   - SCD1（覆盖）：无需保留历史
   - SCD2（追加行）：需保留完整历史变化轨迹
   - SCD3（追加列）：仅保留前一个值
   - 同一维度内不同属性可有不同 SCD 类型（如 user_name 用 SCD1，user_level 用 SCD2）；`scd_strategy` 取该维度中最严格的类型，`scd_columns` 按 `类型:字段` 格式分组记录
6. 产出 `dwm_s4_dim_registry`

### 2.5 组装总线矩阵草稿

1. 创建矩阵骨架：行=业务过程（按 `dwm_s3_subject_area` 分组），列=一致性维度（`dwm_s4_dim_registry`）
2. 逐格填充关联：存在关系标 `✓`，可附关系强度
3. 标记特殊维度：退化维度、低基数离散属性组合维、角色扮演维度
4. 记录备注：不连接原因或后续补建计划
5. 产出 `dwm_bus_matrix`（status=draft）

---

## 3. 产出物（4 张工作底稿）

### 3.1 `dwm_s4_fact_metric`（度量归属底稿）

一行一个度量归属。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
| fact_table | 事实表名 | 是 | 来自 `dwm_s3_table_profile WHERE table_role='fact'` |
| bp_standard_name | 业务过程标准名 | 是 | 事实表对应业务过程 |
| metric_column | 度量字段名 | 是 | 字段英文名 |
| metric_name | 度量名称 | 是 | 字段中文注释 |
| metric_type | 度量标签 | 是 | `可加度量` / `半可加度量` / `不可加度量` |
| agg_suggest | 聚合建议 | 是 | `sum` / `avg` / `max` / `min` / `count_distinct` |
| unit | 度量单位 | 是 | 元 / 件 / % / 次 等 |
| is_derived | 是否派生度量 | 是 | `Y` / `N` |
| derived_logic | 派生逻辑 | 条件 | `is_derived=Y` 时必填 |
| remark | 备注 | 否 | 额外说明 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`fact_table + metric_column`

### 3.2 `dwm_s4_fact_dim_ref`（维度引用底稿）

一行一条引用关系。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
| fact_table | 事实表名 | 是 | 来自 `dwm_s3_table_profile WHERE table_role='fact'` |
| bp_standard_name | 业务过程标准名 | 是 | 事实表对应业务过程 |
| dimension_type | 维度类型 | 是 | `外键` / `退化维度` / `低基数离散属性候选` |
| dimension_column | 维度字段名 | 是 | 字段英文名 |
| dimension_name | 维度名称 | 条件 | `dimension_type=外键` 时必填 |
| ref_table | 引用维表名 | 条件 | `dimension_type=外键` 时必填 |
| ref_column | 引用字段名 | 条件 | `dimension_type=外键` 时必填 |
| is_mandatory | 是否必选维度 | 是 | `Y` / `N` |
| missing_tolerance | 缺失容忍策略 | 是 | 如"匿名用户填充 UNKNOWN" |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`fact_table + dimension_type + dimension_column`

### 3.3 `dwm_s4_dim_registry`（一致性维度底稿）

一行一个一致性维度。产出格式：数据库表 / CSV。仅注册需建 DIM 表的维度。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| dimension_key | 维度唯一标识 | 是 | 命名：`dim_xxx` |
| dimension_name | 维度中文名称 | 是 | 如"用户维度" |
| dimension_desc | 维度描述 | 是 | 一句话业务含义 |
| source_dimension_table | 源维表名 | 是 | 来自 `dwm_s3_table_profile WHERE table_role='dimension'` |
| grain_keys | 粒度键 | 是 | 业务键/代理键字段，逗号分隔 |
| dimension_columns | 维度属性字段 | 是 | 所有维度属性，逗号分隔 |
| modeling_strategy | 建模策略 | 是 | `独立维表` |
| scd_strategy | SCD 策略 | 条件 | 维度级，取最严格类型：`SCD1` / `SCD2` / `SCD3` / `-` |
| scd_columns | SCD 字段列表 | 条件 | `scd_strategy != '-'` 时必填，按类型分组：`SCD2:col1,col2;SCD1:col3` |
| join_columns | 关联字段列表 | 是 | 事实表引用此维度时使用的字段 |
| is_conformed | 是否一致性维度 | 是 | `Y` / `N` |
| conformed_across | 跨事实表一致性说明 | 条件 | `is_conformed=Y` 时必填 |
| remark | 备注 | 否 | 额外说明 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`dimension_key`

### 3.4 `dwm_bus_matrix`（总线矩阵草稿）

二维矩阵，行=业务过程，列=一致性维度。通过 `version` + `status` 管理生命周期（第四步创建 status=draft，第五步验证通过后更新为 status=published）。

产出格式：Excel 表格 / 可视化工具导出。

| 元数据字段 | 说明 |
|-----------|------|
| version | 版本号，如 `v1.0` |
| status | `draft` / `published` |
| updated_by | 最近修改人 |
| updated_at | 最近修改时间 |

矩阵结构：`✓` = 存在关联，`-` = 无关联，空白 = 待确认。

Excel 结构规范：
- Sheet 名：`总线矩阵 v{version}`
- A 列：主题域（`主题域名称(编码)`，每行填充，不做合并）
- B 列：业务过程（中文名，来自 `business_process`）
- C 列：业务过程代码（英文标准名，`bp_standard_name`）
- D 列：粒度声明（来自 `grain_statement`）
- E 列：事实表类型（`fact_type`）
- F 列起：每列一个一致性维度（列头 = `dimension_name`，来自 `dwm_s4_dim_registry`）
- 单元格值：`✓` / `-` / 空
- 末行区域：元数据（version / status / updated_by / updated_at）
- 行按 `bp_standard_name` 去重（一个业务过程 = 一行，不按 ODS 表展开）

### 3.5 派生查询

```sql
-- 技术属性剔除清单
SELECT ods_table_name, col_name, core_tag, reason
FROM dwm_s2_field_tag
WHERE core_tag IN ('技术属性', '技术时间');

-- 无事实表清单（factless）
SELECT ods_table_name, business_process, bp_standard_name
FROM dwm_s3_table_profile
WHERE table_role = 'fact' AND fact_type = 'factless';

-- 复杂属性清单（建设阶段拆解决策输入）
SELECT ods_table_name, col_name, complex_type, col_comm
FROM dwm_s2_field_tag
WHERE ext_tags LIKE '%多值/复杂属性%';
```

---

## 4. 验收标准

1. `dwm_s4_fact_metric` 中每个度量字段已归属，聚合语义与事实表类型匹配
2. `dwm_s4_fact_dim_ref` 中每个业务过程至少有一个核心分析维度外键
3. 外键引用目标明确（`ref_table`/`ref_column` 非空）
4. `dwm_s4_dim_registry` 中每个维度键有唯一口径定义，跨事实无冲突
5. 维度候选池已剔除技术属性/技术时间（占比 = 0）
6. 每个业务过程有明确事实表类型，已回写 `dwm_s3_table_profile.fact_type`
7. 每个一致性维度中的 SCD 属性字段已确认 SCD 类型
8. 矩阵中无"无法说明的 ✓"与"应连未连"

---

## 5. 与下一步衔接

本步 4 张工作底稿 → 第五步合成为最终交付物：

| 工作底稿 | 第五步消费方式 |
|----------|--------------|
| `dwm_s4_fact_metric` + `dwm_s4_fact_dim_ref` | → 合成 `dwm_dwd_fact_spec`（DWD 事实表建设清单） |
| `dwm_s4_dim_registry` | → 合成 `dwm_dim_table_spec`（DIM 维度表建设清单） |
| `dwm_bus_matrix`（draft） | → 验证后发布为 published |
| 以上全部 + `dwm_s3_subject_area` | → 合成 `dwm_subject_area_summary`（主题域清单） |

其他衔接：
- `dwm_s3_table_profile.fact_type` → DWD 事实表建模与 DWS 汇总策略依据
- `dwm_s2_field_tag WHERE ext_tags LIKE '%多值/复杂属性%'` → 建设阶段 DWD 扁平化决策输入
