---
name: cdm-modeling
description: >-
  This skill should be used when the user asks to "CDM建模", "DIM设计", "DWD设计",
  "读取总线矩阵文档生成模型", "读取ODS元数据解析文档", "维度表生成", "事实表生成",
  "SCD策略", "拉链表", "星形模型", "代理键生成", "ETL脚本生成", "建表语句生成",
  or discusses CDM layer modeling from upstream bus-matrix and ODS metadata analysis outputs.
version: 1.3.0
---

# CDM 建模 Skill

读取上游 skill 已经产出的总线矩阵解析文档和 ODS 元数据解析文档，生成 CDM 层 DIM/DWD 数据模型、DDL 建表语句、ETL SQL、字段映射清单和校验报告。

## 使用边界

将本 skill 用于“上游解析已经完成”的建模场景。不要让本 skill 直接重新解析原始 ODS DDL 或手工推导总线矩阵；上游文档才是事实来源。

必需输入：
- **总线矩阵文档**：包含数据域、业务过程、粒度、一致性维度、度量、源表等说明。
- **ODS 元数据解析文档**：包含 ODS 表、字段、类型、注释、主键/外键、时间字段、字段分类等说明。

可选输入：
- **建模配置**：指定默认 SCD、默认事实类型、输出目录、是否生成 DDL/ETL。

## 五步流程总览

| 步骤 | 核心目标 | 关键产出 | Reference |
|-----|---------|---------|-----------|
| 第一步 | 读取并校验上游文档 | 统一建模上下文、输入告警 | `references/step1-upstream-input.md` |
| 第二步 | 生成 DIM 维度设计 | DIM 设计、业务键、属性、SCD 策略 | `references/step2-dim-design.md` |
| 第三步 | 生成 DWD 事实设计 | DWD 设计、粒度、维度外键、度量 | `references/step3-dwd-design.md` |
| 第四步 | 渲染 DDL/ETL 与清单 | SQL、模型清单、字段映射、依赖清单 | `references/step4-generation.md` |
| 第五步 | 执行模型门禁校验 | `validation_report.md`、校验状态 | `references/step5-validation.md` |

流程主线：上游文档 → 统一建模上下文 → DIM → DWD → DDL/ETL/docs → 校验报告。

## 推荐输入格式

优先使用 YAML 或 JSON 格式，因为字段结构稳定，最适合自动生成：

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

Markdown 文档也可以使用，但应包含标准表格列名，例如 `数据域`、`业务过程`、`粒度`、`一致性维度`、`度量`、`源表`。

## 输出约定

默认输出写入 `output/cdm-modeling/`：

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

## 建模流程

1. 读取 `skill_config.yaml` 或命令行传入的 `--config`。
2. 解析上游总线矩阵文档，提取数据域、业务过程、粒度、维度、度量、源表。
3. 解析上游 ODS 元数据文档，提取字段类型、字段注释、字段分类、主键、外键、时间字段。
4. 合并两个上游来源，形成统一建模上下文。
5. 生成 DIM 维度表设计，优先使用上游文档中的维度属性和业务键。
6. 生成 DWD 事实表设计，优先使用总线矩阵文档中的度量和粒度。
7. 渲染 DDL、ETL、模型清单、字段映射、依赖清单和校验报告。

## 关键规则

- 维度属性不得再硬编码为 `{entity}_name` 和 `{entity}_code`；必须优先来自 ODS 元数据解析结果。
- 事实表度量不得再硬编码为 `quantity` 和 `amount`；必须优先来自总线矩阵文档的度量定义。
- SCD 策略优先级：显式配置或上游文档 > ODS 时间字段和状态字段推断 > 默认策略。
- DWD 表粒度必须来自总线矩阵文档；缺失时写入 `validation_report.md`。
- 每个 DWD 事实表必须至少有一个度量；缺失时仍可生成结构草案，但必须在校验报告中标记。
- 每个维度必须有业务键；无法从上游文档或 ODS 元数据推断时使用 `{entity}_id` 并记录告警。

## 详细资料

Reference files:
- **`references/skill_usage.md`** - 完整使用指南和输入格式说明
- **`references/mandatory-modeling-rules.md`** - 必须遵守的 CDM 建模规则
- **`references/field-classification-rules.md`** - 字段分类、类型映射和质量规则
- **`references/scd-lifecycle-rules.md`** - SCD 生命周期和增量类型规则
- **`references/anti-patterns.md`** - 建模反模式和禁止项
- **`references/step1-upstream-input.md`** - 上游输入契约与解析规则
- **`references/step2-dim-design.md`** - DIM 设计步骤、产物和验收标准
- **`references/step3-dwd-design.md`** - DWD 设计步骤、产物和验收标准
- **`references/step4-generation.md`** - DDL/ETL/docs 生成规则
- **`references/step5-validation.md`** - 模型门禁和校验报告规则
- **`references/dim_design_guide.md`** - DIM 维度表设计指南
- **`references/dwd_design_guide.md`** - DWD 事实表设计指南

Legacy rule files:
- **`references/legacy-rules/*.yaml`** - 历史 YAML 规则资料。当前主流程不直接执行这些 YAML；优先读取上述 Markdown 规则文档。

Scripts:
- **`scripts/main.py`** - 主入口
- **`scripts/parse_upstream_outputs.py`** - 上游总线矩阵和 ODS 元数据文档解析
- **`scripts/generate_dim.py`** - DIM 设计和 DDL 生成
- **`scripts/generate_dwd.py`** - DWD 设计和 DDL 生成
- **`scripts/generate_etl.py`** - ETL 脚本生成
- **`scripts/validate_model.py`** - 生成产物门禁校验
