# 第四步：确认事实（Kimball Step 4）

## 0. 本步定位

对应 Kimball 四步法的最后一步：确认事实。先确定事实表类型（驱动度量可加性校验规则），再将度量归属到对应业务过程。

本步产出 2 张工作底稿：

| 工作底稿 | 回答什么问题 | 下游消费 |
|----------|------------|---------|
| `dwm_fct_type` | 每个业务过程的事实表类型是什么？ | → 回写 `dwm_bp_table_profile.fact_type` + ⑤合成 DWD spec |
| `dwm_fct_metric` | 每张事实表有哪些度量、怎么聚合？ | → ⑤合成 DWD 事实表建设清单 |

---

## 1. 输入

| 输入项 | 来源 Skill | 用途 |
|--------|-----------|------|
| `dwm_bp_table_profile WHERE table_role='fact'` | ② | 业务过程清单与粒度声明 |
| `dwm_inv_field_profile` | ① | 字段角色画像（`is_numeric=Y` → 度量候选） |
| `dwm_inv_field_registry` | ① | 字段类型信息 |

---

## 2. 实施步骤

> 如需编写批量度量校验 SQL 脚本或数据处理脚本，use context7 获取对应 SQL 方言（HiveQL / SparkSQL）或 Python 库的最新文档。

### 2.1 确定事实表类型

对每个业务过程确认事实表类型：

| 类型 | fact_type 编码 | 判定依据 | 典型场景 |
|------|---------------|---------|---------|
| 事务事实表 | `transaction` | 一行一笔业务事件，不可变 | 下单、支付、退款 |
| 周期快照事实表 | `periodic_snapshot` | 按固定周期截面记录状态 | 日库存、月账户余额 |
| 累积快照事实表 | `accumulating_snapshot` | 一行跟踪业务全生命周期，多个里程碑时间 | 订单履约 |
| 无事实事实表 | `factless` | 无度量但有业务行为记录 | 用户浏览、签到 |

判定规则：
1. 有明确业务事件时间 + 事件后行不变 → 事务事实表
2. 无明确事件、按周期截面 + 半可加度量 → 周期快照事实表
3. 一行有多个里程碑时间、行随流程推进更新 → 累积快照事实表
4. 无度量但有业务行为记录 → 无事实事实表

产出 `dwm_fct_type`，同时回写 `dwm_bp_table_profile` 的 `fact_type` 和 `fact_type_evidence`。

### 2.2 确定度量

1. 从 `dwm_inv_field_profile WHERE is_numeric='Y' AND field_role='numeric_measure'` 获取度量候选
2. 逐个归属到对应事实表
3. 判定度量可加性类型：

| 度量类型 | metric_type | 判定依据 |
|---------|------------|---------|
| 可加度量 | `可加度量` | 可沿所有维度安全求和（如 amount, qty） |
| 半可加度量 | `半可加度量` | 仅在部分维度可加，通常不可跨时间累加（如 balance, inventory） |
| 不可加度量 | `不可加度量` | 不可求和，宜均值/比率/去重（如 rate, unit_price） |

4. 确认每个度量的 `agg_suggest` 与事实表类型匹配：

| 事实表类型 | 度量特征 |
|-----------|---------|
| `transaction` | 度量通常可加（sum） |
| `periodic_snapshot` | 度量通常半可加（不可跨时间 sum） |
| `accumulating_snapshot` | 里程碑间时间差、状态标志为典型度量 |
| `factless` | 无度量，仅有隐含计数 |

5. 识别派生事实（如 `利润 = 收入 - 成本`），标注计算逻辑，决定存储还是运行时计算
6. 产出 `dwm_fct_metric`

### 2.3 度量可加性校验

| 校验项 | 规则 | 失败处理 |
|--------|-----|---------|
| 可加度量在事务表中 | 可跨所有维度 sum | 通过 |
| 可加度量在快照表中 | 需确认是否为增量而非余额 | 修正为半可加 |
| 半可加度量在事务表中 | 通常不应出现 | 重新检查是否为余额类 |
| 不可加度量的 agg_suggest | 不应为 sum | 修正 agg_suggest |

---

## 3. 产出物

### 3.1 `dwm_fct_type`（事实表类型确认表）

一行一个业务过程。产出格式：CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| ods_table_name | ODS 表名 | 是 | 主键，关联 `dwm_bp_table_profile` |
| bp_standard_name | 业务过程标准名 | 是 | 来自 `dwm_bp_table_profile` |
| fact_type | 事实表类型 | 是 | `transaction` / `periodic_snapshot` / `accumulating_snapshot` / `factless` |
| fact_type_evidence | 类型判定依据 | 是 | 简述判定逻辑 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`ods_table_name`

### 3.2 `dwm_fct_metric`（度量归属底稿）

一行一个度量归属。产出格式：CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| source_code | 数据源编码 | 是 | 关联 `dwm_inv_source_registry` |
| fact_table | 事实表名 | 是 | 来自 `dwm_bp_table_profile WHERE table_role='fact'` |
| bp_standard_name | 业务过程标准名 | 是 | 事实表对应业务过程 |
| metric_column | 度量字段名 | 是 | 字段英文名 |
| metric_name | 度量名称 | 是 | 字段中文注释 |
| metric_type | 度量类型 | 是 | `可加度量` / `半可加度量` / `不可加度量` |
| agg_suggest | 聚合建议 | 是 | `sum` / `avg` / `max` / `min` / `count_distinct` |
| unit | 度量单位 | 是 | 元 / 件 / % / 次 等 |
| is_derived | 是否派生度量 | 是 | `Y` / `N` |
| derived_logic | 派生逻辑 | 条件 | `is_derived=Y` 时必填 |
| remark | 备注 | 否 | 额外说明 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`fact_table + metric_column`

---

## 4. 验收标准

1. 每个 `table_role=fact` 的业务过程有明确 `fact_type`，已回写 `dwm_bp_table_profile`
2. `dwm_fct_metric` 中每个度量字段已归属，聚合语义与事实表类型匹配
3. 可加度量在周期快照表中需二次确认
4. 所有度量字段已填写 `agg_suggest` 与 `unit`
5. 派生度量已标注计算逻辑

---

## 5. 与下一步衔接

- `dwm_fct_type` → ⑤ 合成 DWD 事实表建设清单时使用
- `dwm_fct_metric` → ⑤ 合成 DWD 事实表建设清单的度量字段部分
- `fact_type` 回写 `dwm_bp_table_profile` → 供 ③ 参考（如需确认退化维度是否在事务表中）
