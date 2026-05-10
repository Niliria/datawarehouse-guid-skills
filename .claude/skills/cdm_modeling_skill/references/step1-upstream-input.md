# 第一步：上游输入读取与契约校验

读取总线矩阵解析文档和 ODS 元数据解析文档，形成后续 DIM/DWD 生成所需的统一建模上下文。

执行本步骤时同时参考：
- `references/mandatory-modeling-rules.md`
- `references/field-classification-rules.md`
- `references/anti-patterns.md`

## 1. 输入

| 输入项 | 来源 | 用途 |
|--------|------|------|
| `bus_matrix_doc` | 上游总线矩阵 skill | 提供数据域、业务过程、粒度、维度、度量、源表 |
| `ods_metadata_doc` | 上游 ODS 元数据解析 skill | 提供表、字段、类型、说明、分类、维度归属 |
| `skill_config.yaml` | 本 skill 配置 | 提供输入路径、输出目录、默认建模策略 |

## 2. 支持格式

优先级：YAML/JSON > Markdown fenced YAML/JSON > Markdown 表格。

Markdown 表格应使用稳定列名：

| 文档 | 必要列 |
|------|--------|
| 总线矩阵文档 | `数据域`、`业务过程`、`粒度`、`一致性维度`、`度量`、`源表` |
| ODS 元数据文档 | `表名`、`字段名`、`字段类型`、`字段说明`、`字段分类`、`维度` |

## 3. 统一上下文结构

解析后形成：

```yaml
processes:
  - domain: sales
    business_process: shop_sales
    grain: 订单明细
    dimensions: [客户, 商品, 店铺, 日期]
    measures: [...]
    source_tables: [...]
dimensions:
  - entity: customer
    business_key: customer_id
    attributes: [...]
    scd_type: 2
ods_tables:
  ods_sales_order_detail:
    fields: [...]
warnings: []
```

## 4. 解析规则

1. 仅将显式标注 `dimension` 的字段、外键字段、日期键字段、维度属性字段纳入维度构建。
2. 不从普通 `*_id`、度量字段、技术时间字段自动推导维度，避免误生成维表。
3. 总线矩阵中的维度列表是事实表外键的权威来源。
4. ODS 元数据中的 `dimension_attribute` 是维度属性的权威来源。
5. 总线矩阵中的 `measures` 是事实表度量的权威来源。

## 5. 验收标准

1. 至少解析到一个业务过程。
2. 每个业务过程有 `domain`、`business_process`、`grain`。
3. 每个业务过程有维度列表。
4. 每个业务过程有度量列表，除非明确标记为 `factless`。
5. 每个维度能解析或推断出业务键。
6. 解析告警必须写入 `validation_report.md`。
