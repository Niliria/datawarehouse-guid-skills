# CDM 建模 Skill 使用指南

**版本**: 1.0  
**状态**: ✅ 完全可用  
**更新时间**: 2026年4月9日  

---

## 📚 目录

1. [快速开始](#快速开始)
2. [项目结构](#项目结构)
3. [工作流程](#工作流程)
4. [配置说明](#配置说明)
5. [输出产物](#输出产物)
6. [常见问题](#常见问题)
7. [最佳实践](#最佳实践)

---

## 🚀 快速开始

### 5分钟快速上手

#### 1️⃣ 准备输入文件

在 `input/` 目录中准备两个文件：

**总线矩阵** (`input/bus_matrix.csv`):
```csv
数据域,业务过程,粒度,一致性维度,备注
销售,门店销售,订单,店铺+日期+商品+客户,按订单粒度
销售,订单退货,退货,店铺+日期+商品+客户,
库存,商品库存,库存变动,店铺+日期+商品,
```

**ODS元数据** (`input/ods_metadata/*.sql` - 可选):
- `sales.sql` - 销售相关ODS表
- `inventory.sql` - 库存相关ODS表

#### 2️⃣ 修改配置（可选）

编辑 `skill_config.yaml` 调整：
- 输出目录
- DDL/ETL生成选项
- SCD策略
- 规则和模板位置

#### 3️⃣ 运行Skill

```bash
cd cdm_modeling_skill
python scripts/main.py
```

#### 4️⃣ 查看输出

```bash
# 查看生成的DDL
ls -la output/ddl/dim/    # → dim_*.sql
ls -la output/ddl/dwd/    # → dwd_*.sql

# 查看生成的ETL
ls -la output/etl/dim/    # → load_dim_*.sql
ls -la output/etl/dwd/    # → load_dwd_*.sql

# 查看设计文档
cat output/docs/model_design.md
cat output/dim_list.csv   # 表清单
```

---

## 📁 项目结构

### 新架构的清晰性

```
cdm_modeling_skill/
│
├── skill_config.yaml                    # ⭐ 单一入口配置
│
├── input/                               # 📥 用户输入
│   ├── bus_matrix.csv                   # 总线矩阵（用户提供）
│   └── ods_metadata/
│       └── *.sql                        # ODS建表语句（参考）
│
├── rules/                               # 📋 分离的业务规则
│   ├── naming_rules.yaml                # 命名规范
│   ├── dim_rules.yaml                   # DIM建模规则
│   ├── dwd_rules.yaml                   # DWD建模规则
│   ├── type_mapping.yaml                # 字段类型映射
│   └── lifecycle_rules.yaml             # 生命周期(SCD)规则
│
├── templates/                           # 📄 独立的代码模板
│   ├── dim_ddl.tpl                      # DIM建表模板
│   ├── dwd_ddl.tpl                      # DWD建表模板
│   ├── dim_etl.tpl                      # DIM ETL模板
│   ├── dwd_etl.tpl                      # DWD ETL模板
│   └── scd_type2.tpl                    # SCD II拉链表模板
│
├── scripts/                             # 🐍 单一职责的脚本
│   ├── main.py                          # 主入口与协调
│   ├── parse_bus_matrix.py              # 解析总线矩阵
│   ├── generate_dim.py                  # 生成DIM表设计
│   ├── generate_dwd.py                  # 生成DWD表设计
│   └── generate_etl.py                  # 生成ETL脚本
│
├── output/                              # 📤 自动生成的产物
│   ├── ddl/
│   │   ├── dim/                         # DIM建表SQL
│   │   └── dwd/                         # DWD建表SQL
│   ├── etl/
│   │   ├── dim/                         # DIM加载脚本
│   │   └── dwd/                         # DWD加载脚本
│   ├── docs/                            # 设计文档
│   ├── dim_list.csv                     # DIM表清单
│   ├── dwd_list.csv                     # DWD表清单
│   └── dependency.csv                   # 调度依赖
│
└── docs/                                # 📚 文档
    ├── README.md                        # 项目说明
    ├── skill_usage.md                   # 本文件
    ├── dim_design_guide.md              # DIM设计指南
    └── dwd_design_guide.md              # DWD设计指南
```

### 关键改进

| 方面 | 旧架构 | 新架构 | 优势 |
|-----|-------|-------|------|
| **配置** | 4个杂乱的YAML | `skill_config.yaml` 统一入口 | 配置集中 |
| **规则** | `config/` 混合 | 分离的 `rules/` | 职责清晰 |
| **模板** | 内嵌在代码中 | 独立的 `templates/*.tpl` | 易于修改 |
| **脚本** | 一个大的generator.py | 5个单一职责脚本 | 可维护性高 |
| **输出** | 平铺的ddl/etl | 分层的 ddl/dim/, etl/dim/ | 易于查找 |

---

## 🔄 工作流程

### 完整执行流程

```
Step 1: 用户准备
├── 编写 bus_matrix.csv
├── 准备 ods_metadata/*.sql (可选)
└── 修改 skill_config.yaml

Step 2: 执行Skill
├── python scripts/main.py
│   ├── Phase 1: 解析总线矩阵
│   ├── Phase 2: 解析ODS元数据 (可选)
│   ├── Phase 3: 生成DIM维度表设计
│   ├── Phase 4: 生成DWD事实表设计
│   ├── Phase 5: 生成ETL加载脚本
│   └── Phase 6: 生成设计文档

Step 3: 验证输出
├── output/ddl/dim/*.sql     → DDL语句
├── output/ddl/dwd/*.sql     → DDL语句
├── output/etl/dim/*.sql     → ETL脚本
├── output/etl/dwd/*.sql     → ETL脚本
├── output/dim_list.csv      → 表清单
└── output/dependency.csv    → 依赖关系

Step 4: 执行SQL
├── 执行 output/ddl/dim/*.sql 创建维度表
├── 执行 output/ddl/dwd/*.sql 创建事实表
├── 执行 output/etl/dim/*.sql 加载维度数据
└── 执行 output/etl/dwd/*.sql 加载事实数据
```

### 数据流向

```
总线矩阵 (CSV)
  ↓
[Phase 1: 解析]
  ↓
业务过程 + 一致性维度
  ↓
[Phase 3-4: 设计生成]
  ├→ DIM维度表设计 (SCD处理)
  └→ DWD事实表设计 (星形结构)
  ↓
[Phase 5: SQL生成]
  ├→ output/ddl/dim/ (建表语句)
  ├→ output/ddl/dwd/ (建表语句)
  ├→ output/etl/dim/ (SCD逻辑)
  └→ output/etl/dwd/ (JOIN维度)
  ↓
[Phase 6: 文档]
  └→ output/docs/ + output/*_list.csv
```

---

## ⚙️ 配置说明

### skill_config.yaml 详解

#### 1. 输入配置 (`input`)

```yaml
input:
  bus_matrix: "input/bus_matrix.csv"    # 总线矩阵文件
  ods_metadata: "input/ods_metadata/"   # ODS元数据目录
```

**bus_matrix.csv 格式**:
```
数据域,业务过程,粒度,一致性维度,备注
销售,订单,订单,店铺+日期+商品+客户,订单粒度的销售事实
```

#### 2. 规则配置 (`rules`)

五个规则文件分别控制不同方面：

| 规则文件 | 控制内容 | 典型配置 |
|---------|---------|---------|
| `naming_rules.yaml` | 表名/字段名规范 | layer_prefix, column_suffix |
| `dim_rules.yaml` | DIM表设计 | 代理键、属性、SCD字段 |
| `dwd_rules.yaml` | DWD表设计 | 维度外键、度量值、粒度 |
| `type_mapping.yaml` | 字段分类 | 如何识别度量、属性、键值 |
| `lifecycle_rules.yaml` | SCD处理 | Type I/II/III 判断规则 |

#### 3. 模板配置 (`templates`)

五个模板文件是SQL生成的基础：

| 模板文件 | 生成内容 |
|---------|--------|
| `dim_ddl.tpl` | DIM建表语句 (含SCD字段) |
| `dwd_ddl.tpl` | DWD建表语句 (星形结构) |
| `dim_etl.tpl` | DIM加载脚本 (SCD逻辑) |
| `dwd_etl.tpl` | DWD加载脚本 (JOIN维度) |
| `scd_type2.tpl` | SCD Type II拉链表实现 |

#### 4. 建模策略 (`modeling`)

```yaml
modeling:
  dimensions:
    auto_create: true           # 为每个一致性维度创建DIM表
    default_scd_strategy: "auto" # 自动判断SCD类型
  facts:
    auto_create: true           # 为每个业务过程创建DWD表
    granularity: "finest"       # 选择最细粒度
```

---

## 📤 输出产物详解

### 1. DDL产物

#### dim/*.sql - 维度表建表语句

```sql
CREATE TABLE dim_customer_scd2 (
    customer_sk BIGINT,
    customer_id BIGINT,
    customer_name STRING,
    ...
    begin_date STRING,
    end_date STRING,
    is_active INT
)
PARTITIONED BY (pt STRING)
STORED AS ORC;
```

**特点**:
- ✅ 包含代理键 (customer_sk)
- ✅ 包含业务键 (customer_id)
- ✅ 包含SCD字段 (begin_date/end_date/is_active)
- ✅ 按分区日期 (pt) 分区

#### dwd/*.sql - 事实表建表语句

```sql
CREATE TABLE dwd_sales_order_di (
    order_id STRING,
    order_sk BIGINT,
    customer_sk BIGINT,      -- 到 dim_customer 的外键
    product_sk BIGINT,       -- 到 dim_product 的外键
    shop_sk BIGINT,          -- 到 dim_shop 的外键
    date_sk BIGINT,          -- 到 dim_date 的外键
    order_amount DECIMAL(18,2),
    quantity BIGINT,
    ...
)
PARTITIONED BY (pt STRING)
STORED AS ORC;
```

**特点**:
- ✅ 星形结构：所有维度通过SK外键指向
- ✅ 度量值：可以SUM、COUNT、AVG
- ✅ 按分区日期 (pt) 分区

### 2. ETL产物

#### dim/*.sql - 维度加载脚本

```sql
-- 示例：DIM Type II 拉链表加载
INSERT OVERWRITE TABLE dim_customer_scd2
SELECT 
    ROW_NUMBER() OVER (...) AS customer_sk,
    customer_id,
    customer_name,
    ...
    '${PT_DATE}' AS begin_date,
    '9999-12-31' AS end_date,
    1 AS is_active
FROM dws_dim_customer_di
WHERE pt = '${PT_DATE}';
```

**特点**:
- ✅ 从 dws_dim_* 表读取
- ✅ 自动生成代理键 (ROW_NUMBER OVER)
- ✅ 包含参数化 (${PT_DATE})
- ✅ SCD逻辑已实现（拉链表处理）

#### dwd/*.sql - 事实加载脚本

```sql
-- 示例：DWD事实表加载 (JOIN维度)
INSERT OVERWRITE TABLE dwd_sales_order_di
SELECT
    source.order_id,
    ROW_NUMBER() OVER (...) AS order_sk,
    dim_customer.customer_sk,      -- JOIN维度获取SK
    dim_product.product_sk,        -- 
    dim_shop.shop_sk,              --
    dim_date.date_sk,              --
    source.order_amount,
    source.quantity,
    ...
FROM dws_sales_order_di source
LEFT JOIN dim_customer ON source.customer_id = dim_customer.customer_id
LEFT JOIN dim_product ON source.product_id = dim_product.product_id
LEFT JOIN dim_shop ON source.shop_id = dim_shop.shop_id
LEFT JOIN dim_date ON source.order_date = dim_date.calendar_date
WHERE source.pt = '${PT_DATE}';
```

**特点**:
- ✅ 从 dws_* 表 + 维度表 JOIN 读取
- ✅ 自动匹配维度键值
- ✅ 生成星形结构
- ✅ 参数化，支持增量加载

### 3. 元表产物

#### dim_list.csv - 维度表清单

```csv
表名,实体,SCD类型,业务键,估计大小,生命周期(天)
dim_customer,customer,2,customer_id,small,9999
dim_product,product,2,product_id,small,9999
dim_shop,shop,1,shop_id,small,9999
```

#### dwd_list.csv - 事实表清单

```csv
表名,业务过程,粒度,维度数,度量数,估计大小
dwd_sales_order_di,订单,order_id,4,2,large
```

#### dependency.csv - 调度依赖

```csv
层级,源表,依赖表,加载顺序,说明
DIM,dim_*,dws_dim_*,2,维度表从dws加载
DWD,dwd_*,dim_*+dws_*,3,事实表join维度和dws
```

---

## ❓ 常见问题

### Q1: 如何自定义SCD策略？

在 `lifecycle_rules.yaml` 中修改自动判断规则，或在 `bus_matrix.csv` 的备注中显式标记：

```csv
数据域,业务过程,粒度,一致性维度,备注
销售,订单,订单,店铺+日期+商品+客户,客户维度(Type II)
```

### Q2: 如何添加新的度量字段？

在 `dwd_rules.yaml` 中修改度量识别规则，或在ODS的COMMENT中标记：

```sql
CREATE TABLE ods_sales_order (
    order_id BIGINT,
    order_amount DECIMAL(18,2) COMMENT '订单总额(可加总)',  -- 标记为度量
    ...
);
```

### Q3: 如何修改自动生成的SQL？

1. 生成后在 `output/ddl/` 或 `output/etl/` 中直接修改
2. 或修改对应的模板 `templates/*.tpl`，重新执行生成

### Q4: 生成的SQL能直接执行吗？

大部分可以，但建议：
1. 检查表名、字段名是否符合实际业务
2. 验证维度和事实表的定义是否正确
3. 调整 ORC 压缩、生命周期等参数
4. 在开发环境测试后再执行

### Q5: 如何集成到CI/CD？

```bash
#!/bin/bash
cd cdm_modeling_skill
python scripts/main.py

# 验证输出
if [ -d "output/ddl/dim" ] && [ -d "output/etl/dim" ]; then
    echo "✅ 生成成功"
    # 部署到Hive
    for file in output/ddl/*/*.sql; do
        hive -f "$file"
    done
else
    echo "❌ 生成失败"
    exit 1
fi
```

---

## 🎓 最佳实践

### 1. 输入规范

✅ **总线矩阵格式统一**
```csv
数据域,业务过程,粒度,一致性维度,备注
销售,订单,订单,店铺+日期+商品+客户,订单粒度
```

❌ **避免不规范格式**
```csv
domain,process,grain,dims,note  # 不同的列名
SALES,ORDER,订单,shop,date     # 中英文混合
```

### 2. 总线矩阵设计

✅ **使用体系化的一致性维度**
- 销售域：客户 + 商品 + 店铺 + 日期
- 库存域：商品 + 店铺 + 日期

❌ **避免维度冗余或遗漏**
- 不要为每个过程创建不同的客户维度
- 确保 cross-process 分析的维度一致

### 3. 规则定制

✅ **按业务需求定制规则**
```yaml
# 如果客户等级变化不需要追踪
lifecycle_rules.yaml 中标记客户为 Type I
```

✅ **保持规则集中管理**
```
所有规则在 rules/ 中统一存储和维护
```

❌ **避免散落的定制**
- 不要在每个脚本中独立判断
- 保持 rules/ 为单一真实源 (SPoT)

### 4. 输出管理

✅ **定期查看和存档输出**
```bash
# 备份设计
cp -r output/docs output/docs_backup_$(date +%Y%m%d)

# 版本控制
git add output/
git commit -m "CDM models updated for v1.0"
```

❌ **避免直接修改生成的SQL**
- 修改应在规则或模板层面
- 保持traceable的生成过程

### 5. 性能优化

✅ **根据数据量调整**
```yaml
skill_config.yaml:
  sql_generation:
    etl_script:
      batch_size: 10000  # 根据数据量调整
```

✅ **使用分区策略**
```sql
PARTITIONED BY (pt STRING)  -- 每天一个分区
```

---

## 📞 支持

- 📖 详细文档：[README.md](README.md)
- 🎯 DIM设计指南：[dim_design_guide.md](dim_design_guide.md)
- 🎯 DWD设计指南：[dwd_design_guide.md](dwd_design_guide.md)
- ⚙️ 规则详解：查看 `rules/` 中各个YAML文件

---

**祝你使用愉快！✨**
