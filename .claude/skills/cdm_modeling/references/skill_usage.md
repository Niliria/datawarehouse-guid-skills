# CDM 建模 Skill 使用指南

版本: 1.3.0  
定位: 读取上游总线矩阵解析文档和 ODS 元数据解析文档，生成 CDM 层 DIM/DWD 模型产物。

## 五步流程

| 步骤 | 说明 | 详细文档 |
|-----|------|----------|
| 第一步 | 上游输入读取与契约校验 | `references/step1-upstream-input.md` |
| 第二步 | DIM 维度设计 | `references/step2-dim-design.md` |
| 第三步 | DWD 事实设计 | `references/step3-dwd-design.md` |
| 第四步 | DDL/ETL 与文档产物生成 | `references/step4-generation.md` |
| 第五步 | 模型门禁校验 | `references/step5-validation.md` |

## 输入

本 skill 不再直接读取原始 `bus_matrix.csv` 或 `ods_metadata/*.sql`。输入来源改为上游 skill 的解析结果：

- `bus_matrix_doc`: 总线矩阵解析文档，包含数据域、业务过程、粒度、一致性维度、度量、源表。
- `ods_metadata_doc`: ODS 元数据解析文档，包含表、字段、类型、说明、字段分类、维度归属。

推荐使用 YAML 或 JSON。Markdown 文档也可读取，但需要包含标准表格。

## 规则文档

执行建模时优先参考这些规则文档：

- `references/mandatory-modeling-rules.md`: 强制建模规则，冲突时优先级最高。
- `references/field-classification-rules.md`: 字段分类、类型映射、质量检查。
- `references/scd-lifecycle-rules.md`: SCD 策略和增量类型判断。
- `references/anti-patterns.md`: 反模式和禁止项。

历史 YAML 规则已迁移到 `references/legacy-rules/`。这些 YAML 当前不被主流程直接执行，仅作为追溯资料。

## 配置

默认配置文件位于 skill 根目录 `skill_config.yaml`：

```yaml
input:
  bus_matrix_doc: "examples/basic/bus_matrix_doc.yaml"
  ods_metadata_doc: "examples/basic/ods_metadata_doc.yaml"

output:
  target_dir: "output/cdm-modeling"

modeling:
  default_scd_type: 1
  default_fact_type: "transaction"
  generate_ddl: true
  generate_etl: true
```

也可以通过命令行传入配置：

```bash
python scripts/main.py --config path/to/skill_config.yaml
```

## 总线矩阵文档格式

YAML 示例：

```yaml
processes:
  - domain: 销售
    business_process: 门店销售
    grain: 订单明细
    fact_type: transaction
    dimensions: [客户, 商品, 店铺, 日期]
    measures:
      - name: quantity
        source_field: sale_qty
        type: BIGINT
        description: 销售数量
        aggregation: SUM
      - name: amount
        source_field: sale_amount
        type: DECIMAL(18,2)
        description: 销售金额
        aggregation: SUM
    source_tables: [ods_sales_order_detail]
```

Markdown 表格至少包含这些列：

```markdown
| 数据域 | 业务过程 | 粒度 | 一致性维度 | 度量 | 源表 |
|---|---|---|---|---|---|
| 销售 | 门店销售 | 订单明细 | 客户+商品+店铺+日期 | 销售数量+销售金额 | ods_sales_order_detail |
```

## ODS 元数据解析文档格式

YAML 示例：

```yaml
tables:
  - table_name: ods_sales_order_detail
    domain: 销售
    fields:
      - name: customer_id
        type: STRING
        description: 客户ID
        classification: foreign_key
        dimension: 客户
      - name: customer_name
        type: STRING
        description: 客户名称
        classification: dimension_attribute
        dimension: 客户
      - name: sale_amount
        type: DECIMAL(18,2)
        description: 销售金额
        classification: measure
```

字段分类建议值：

- `business_key`: 业务主键
- `foreign_key`: 维度外键
- `dimension_attribute`: 维度属性
- `date_key`: 日期维度键
- `measure`: 度量
- `create_time` / `update_time`: 生命周期判断字段

## 执行

在 skill 根目录执行：

```bash
python scripts/main.py
```

使用自定义配置：

```bash
python scripts/main.py --config examples/basic/skill_config.yaml
```

独立校验生成产物：

```bash
python scripts/validate_model.py output/cdm-modeling --write-report
```

## 输出

默认输出目录为 `output/cdm-modeling/`：

```text
output/cdm-modeling/
├── ddl/
│   ├── dim/
│   └── dwd/
├── etl/
│   ├── dim/
│   └── dwd/
└── docs/
    ├── dim_list.csv
    ├── dwd_list.csv
    ├── field_mapping.csv
    ├── dependency.csv
    ├── model_design.md
    └── validation_report.md
```

## 生成规则

- DIM 属性优先来自 `ods_metadata_doc` 中标记为 `dimension_attribute` 的字段。
- DIM 业务键优先来自对应维度的 `_id`、`business_key`、`foreign_key` 或 `date_key` 字段。
- DWD 度量优先来自 `bus_matrix_doc` 中的 `measures`。
- DWD 粒度优先来自 `bus_matrix_doc` 中的 `grain`。
- SCD 策略优先使用上游文档中的显式值；没有显式值时，根据日期维度和更新时间字段推断；再缺失时使用配置默认值。

## 校验重点

执行后先查看 `docs/validation_report.md`。报告状态分为：

- `PASS`: 无错误，无告警
- `WARN`: 有告警，可审查但需要说明
- `FAIL`: 有错误，不应进入下游建设

如果报告中出现以下问题，应回到上游文档补充信息：

- 业务过程缺少粒度
- 业务过程缺少维度
- 业务过程缺少度量
- 维度缺少业务键
- 维度缺少属性字段
- DWD 引用了不存在的 DIM
- SQL 文件残留未渲染模板占位符
