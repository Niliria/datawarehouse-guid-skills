---
name: cdm-modeling
description: >-
  This skill should be used when the user asks to "CDM建模", "DIM设计", "DWD设计",
  "维度表生成", "事实表生成", "总线矩阵转DDL", "SCD策略", "拉链表", "星形模型",
  "代理键生成", "ETL脚本生成", "建表语句生成",
  or discusses CDM (Common Data Model) layer modeling based on Kimball dimension modeling methodology.
version: 1.0.0
---

# CDM 建模 Skill

基于《数据仓库工具箱》(Kimball) 维度建模方法论，从总线矩阵和 ODS 元数据快速生成 DIM/DWD 层的数据模型、DDL 建表语句和 ETL SQL。

## 核心能力

- **自动解析总线矩阵** - 识别业务过程、一致性维度关系
- **智能生成 DIM 维度表** - 支持 SCD Type I/II/III 策略
- **智能生成 DWD 事实表** - 星形结构、维度外键、度量值
- **自动输出 DDL 脚本** - 建表语句、分区策略、ORC 存储格式
- **自动输出 ETL 脚本** - 数据加载、SCD 处理、质量检查
- **生成模型清单** - CSV 格式的表清单和元数据

## 输入约定

### 总线矩阵 (bus_matrix.csv)

必需输入，定义业务过程与一致性维度的关系：

```csv
数据域,业务过程,粒度,一致性维度,备注
销售,门店销售,订单,店铺+日期+商品+客户,订单粒度
库存,库存变动,库存变动,店铺+日期+商品,
商品,商品管理,商品,商品,维度表
```

### ODS 元数据 (ods_metadata/*.sql)

可选输入，提供源表字段信息用于智能识别维度属性和度量值。

## 输出约定

执行后产出写入项目 `output/cdm-modeling/` 目录：

```
output/cdm-modeling/
├── ddl/
│   ├── dim/                     # DIM 建表 SQL
│   └── dwd/                     # DWD 建表 SQL
├── etl/
│   ├── dim/                     # DIM ETL 脚本
│   └── dwd/                     # DWD ETL 脚本
└── docs/
    ├── dim_list.csv             # 维度表清单
    ├── dwd_list.csv             # 事实表清单
    └── dependency.csv           # 调度依赖
```

## SCD 策略选择

| SCD 类型 | 适用场景 | 特点 |
|---------|---------|------|
| Type I | 无需历史追踪 | 直接覆盖，无版本字段 |
| Type II | 需完整历史追踪 | 拉链表，含 begin_date/end_date/is_active |
| Type III | 仅需前一值对比 | 含 current_value/prior_value |

**决策矩阵**：

| 业务需求 | 数据质量 | 表大小 | 推荐 SCD |
|---------|---------|--------|---------|
| 需要历史 | 有时间戳 | <100万行 | Type II |
| 需要历史 | 有时间戳 | >100万行 | Type II+分区 |
| 仅需前值 | 有时间戳 | <100万行 | Type III |
| 不需历史 | 任意 | 任意 | Type I |

## DIM 维度表设计规则

### 必需元素

1. **业务键** (`{entity}_id`) - 来自 ODS 的唯一标识
2. **代理键** (`{entity}_sk`) - 系统生成，用于事实表外键
3. **维度属性** - 描述性字段（名称、类别、层级等）
4. **SCD 字段** - 按策略添加版本追踪字段

### 建表模板

```sql
CREATE TABLE IF NOT EXISTS dim_customer (
    -- 维度键
    customer_sk BIGINT COMMENT '代理键(维度主键)',
    customer_id STRING COMMENT '业务键(来自ODS)',
    
    -- 维度属性
    customer_name STRING COMMENT '客户名称',
    customer_level STRING COMMENT '客户等级',
    
    -- SCD II 字段(可选)
    begin_date STRING COMMENT '生效日期(YYYY-MM-DD)',
    end_date STRING COMMENT '失效日期(当前记录为9999-12-31)',
    is_active INT COMMENT '是否当前记录(1=当前,0=历史)',
    
    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间'
)
PARTITIONED BY (pt STRING COMMENT '分区日期')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');
```

## DWD 事实表设计规则

### 必需元素

1. **事实键** - 业务键 + 代理键
2. **维度外键** - 指向各 DIM 表的 `{dim}_sk`
3. **度量值** - 可聚合的数值字段（数量、金额）
4. **业务标志** - 记录有效性标识

### 建表模板

```sql
CREATE TABLE IF NOT EXISTS dwd_sales_order_di (
    -- 事实键
    order_id STRING COMMENT '业务键(来自ODS)',
    order_sk BIGINT COMMENT '代理键(事实主键)',
    
    -- 维度外键
    customer_sk BIGINT COMMENT '→ dim_customer(外键)',
    product_sk BIGINT COMMENT '→ dim_product(外键)',
    shop_sk BIGINT COMMENT '→ dim_shop(外键)',
    date_sk BIGINT COMMENT '→ dim_date(外键)',
    
    -- 度量值
    quantity BIGINT COMMENT '数量(聚合:SUM)',
    amount DECIMAL(18,2) COMMENT '金额(聚合:SUM)',
    
    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间'
)
PARTITIONED BY (pt STRING COMMENT '分区日期')
STORED AS ORC;
```

## 详细规格

For complete field definitions, SCD decision tree, naming conventions, and SQL templates:
- **`references/dim_design_guide.md`** — DIM 维度表设计指南
- **`references/dwd_design_guide.md`** — DWD 事实表设计指南
- **`references/skill_usage.md`** — 完整使用指南

For rule definitions:
- **`rules/naming_rules.yaml`** — 命名规范
- **`rules/dim_rules.yaml`** — DIM 建模规则（含 SCD 决策矩阵）
- **`rules/dwd_rules.yaml`** — DWD 建模规则
- **`rules/type_mapping.yaml`** — 字段类型映射
- **`rules/lifecycle_rules.yaml`** — SCD 生命周期规则

For SQL templates:
- **`templates/dim_ddl.tpl`** — DIM 建表模板
- **`templates/dwd_ddl.tpl`** — DWD 建表模板
- **`templates/dim_etl.tpl`** — DIM ETL 模板
- **`templates/dwd_etl.tpl`** — DWD ETL 模板
- **`templates/scd_type2.tpl`** — SCD II 拉链表模板