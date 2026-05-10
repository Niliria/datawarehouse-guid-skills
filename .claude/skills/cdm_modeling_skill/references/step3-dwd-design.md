# 第三步：DWD 事实设计

根据总线矩阵文档中的业务过程生成 DWD 事实表设计。DWD 的粒度、维度和度量以总线矩阵文档为权威来源。

执行本步骤时同时参考：
- `references/mandatory-modeling-rules.md`
- `references/field-classification-rules.md`
- `references/scd-lifecycle-rules.md`
- `references/anti-patterns.md`

## 1. 输入

| 输入项 | 来源 | 用途 |
|--------|------|------|
| `processes` | 第一步统一上下文 | 业务过程、粒度、维度、度量、源表 |
| `dim_designs` | 第二步输出 | 维度业务键、维度表名 |
| `modeling.default_fact_type` | 配置 | 无显式事实类型时默认值 |

## 2. 实施步骤

1. 为每个业务过程生成一张 DWD 表。
2. 表名格式：`dwd_{domain}_{business_process}_di`。
3. 粒度键优先来自 `grain`，无法映射时使用 `{business_process}_id`。
4. 维度外键来自总线矩阵维度列表，并映射到对应 DIM 的业务键。
5. 度量字段来自总线矩阵 `measures`，保留 `source_field`、`type`、`aggregation`。
6. 日期维度缺失时默认补充 `date`。

## 3. 事实类型

| 类型 | 适用场景 | 说明 |
|------|----------|------|
| `transaction` | 一行一笔业务事件 | 订单、支付、退款 |
| `periodic_snapshot` | 固定周期状态截面 | 日库存、月余额 |
| `accumulating_snapshot` | 一行跟踪生命周期 | 订单履约、审批流程 |
| `factless` | 无数值度量的行为事实 | 登录、曝光、签到 |

## 4. 产出物

### DWD 设计字典

| 字段 | 说明 |
|------|------|
| `table_name` | 事实表名 |
| `domain` | 数据域英文名 |
| `business_process` | 业务过程英文名 |
| `grain` | 事实表粒度 |
| `fact_type` | 事实类型 |
| `dimensions` | 维度实体列表 |
| `dimension_refs` | 维度实体与业务键映射 |
| `measures` | 度量列表 |
| `source_tables` | 来源表列表 |

## 5. 验收标准

1. 每个 DWD 必须有明确粒度。
2. 每个非 `factless` DWD 至少有一个度量。
3. 每个维度外键必须能映射到 DIM 业务键；无法映射时写入校验告警。
4. 度量必须包含字段名、来源字段、类型和聚合建议。
5. DDL/ETL 渲染后不得残留 Jinja 占位符。
