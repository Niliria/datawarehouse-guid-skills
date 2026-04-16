# ① 数据盘点：数据源接入、ODS 盘点、字段元数据采集、字段客观画像

完成"有哪些数据源"、"源里有哪些表/字段"和"每个字段的客观画像"三件事，为后续建模步骤提供输入基座。

---

## 1. 输入

| 输入项 | 说明 | 格式 |
|--------|------|------|
| 系统接入清单 | 数据库/接口/文件等数据源清单 | 文档 / 电子表格 |
| 连接参数与访问凭证 | 数据库连接串、API token、文件路径等 | 安全存储 |
| 基础网络与权限信息 | 网络白名单、访问权限配置 | 安全存储 |
| 目标 ODS 命名规则 | 数据库/表/字段命名规范 | 文档 |
| 小样本数据（建议最近 7~30 天） | 用于字段画像统计（唯一率/空值率/基数） | 查询结果 |

---

## 2. 实施步骤

### 2.1 数据源登记

1. 按"一个独立来源一行"建立 `dwm_inv_source_registry`
2. 填写技术属性：`source_code` / `source_type` / `conn_info` / `charset` / `table_count` / `status` / `registered_at`
3. 评估元数据完整度：`has_ddl` / `has_constraint` / `has_comment` / `completeness_level` / `fallback_strategy`
4. 业务属性暂留空：`owner`（第二步回填）；`source_desc` 已知时直接填写
5. 校验唯一性：`source_code` 全局唯一

### 2.2 ODS 表盘点

1. 按数据源类型采集对象清单（数据库查元数据；API/文件人工梳理）
2. 生成 `dwm_inv_ods_inventory`
3. 判断同步方式：优先全量，满足增量边界且收益显著再用增量
4. 标准化分区策略：T+1 表统一 `dt` 分区

### 2.3 源系统元数据采集（字段清单）

为字段画像提供"证据链"的最高优先级输入。

#### 采集内容

1. **表结构定义**：DDL 语句或 CREATE TABLE 脚本
2. **约束信息**：主键(PK)、唯一键(UK)、外键(FK)、索引(INDEX)
3. **字段注释**：COMMENT / DESCRIPTION / 接口文档说明
4. **字段属性**：数据类型、是否可空、默认值、字符集

#### 采集方式

> 如需编写数据源元数据采集脚本，use context7 获取对应数据库驱动/SDK 的最新文档。

| 数据源类型 | 采集方式 | 输出格式 |
|-----------|---------|---------|
| MySQL | `SHOW CREATE TABLE` / `information_schema.KEY_COLUMN_USAGE` | DDL + 约束清单 |
| PostgreSQL | `pg_dump --schema-only` / `pg_constraint` | DDL + 约束清单 |
| Oracle | `DBMS_METADATA.GET_DDL` / `USER_CONSTRAINTS` | DDL + 约束清单 |
| SQL Server | `sp_help` / `sys.foreign_keys` | DDL + 约束清单 |
| API 接口 | 接口文档 / Swagger / 字段说明 | 字段清单 |
| CSV/日志文件 | 文件头 / 数据字典 / 业务文档 | 字段清单 |

#### 元数据缺失应对

| 完整度等级 | 判定条件 | 后续画像策略 |
|-----------|---------|------------|
| 完整 | DDL + 约束 + 注释齐全 | 标准流程（源约束优先） |
| 部分 | 有 DDL，无约束或注释不全 | 降级流程（画像 + 命名） |
| 缺失 | 仅表名，无结构信息 | 快速模式（仅确定性字段） |

缺失时的补救措施：
1. 联系源系统 DBA/开发获取文档
2. 通过 ODS 数据反推（唯一率/空值率）
3. 业务访谈（仅核心表关键字段）
4. 标记"待补充"，不阻塞后续流程

### 2.4 字段客观画像

对每张 ODS 表的每个字段执行统计分析，赋予 7 种客观角色之一，填充画像属性。

> 如需编写批量画像统计 SQL 脚本，use context7 获取对应 SQL 方言（HiveQL/SparkSQL/Presto 等）的最新文档。

#### 画像统计 SQL 模板

```sql
-- 字段基础画像（唯一率 / 空值率 / 基数）
SELECT
  COUNT(*) AS total_cnt,
  COUNT(DISTINCT ${col}) AS distinct_cnt,
  ROUND(COUNT(DISTINCT ${col}) / COUNT(*), 6) AS distinct_rate,
  SUM(CASE WHEN ${col} IS NULL THEN 1 ELSE 0 END) AS null_cnt,
  ROUND(SUM(CASE WHEN ${col} IS NULL THEN 1 ELSE 0 END) / COUNT(*), 6) AS null_rate,
  MIN(CAST(${col} AS STRING)) AS min_val,
  MAX(CAST(${col} AS STRING)) AS max_val
FROM ${ods_table}
WHERE dt BETWEEN '${start_dt}' AND '${end_dt}';

-- 外键 JOIN 命中率（针对 foreign_key 候选字段）
SELECT
  COUNT(1) AS ref_cnt,
  SUM(CASE WHEN b.${ref_col} IS NULL THEN 1 ELSE 0 END) AS miss_cnt,
  ROUND(SUM(CASE WHEN b.${ref_col} IS NULL THEN 1 ELSE 0 END) / COUNT(1), 4) AS miss_rate
FROM ${fact_table} a
LEFT JOIN ${dim_table} b ON a.${fk_col} = b.${ref_col}
WHERE a.${fk_col} IS NOT NULL
  AND a.dt BETWEEN '${start_dt}' AND '${end_dt}';
```

#### 7 种客观角色

客观角色基于元数据 + 画像统计自动判定，无需人工主观标注。优先级从上到下：

| field_role | 判定规则 | 补充说明 |
|-----------|---------|---------|
| `tech_meta` | 命名命中技术白名单（`etl_*`、`sync_*`、`op_type`、`batch_id`、`insert_time`、`load_*`、`is_deleted` 等） | 最高优先级，直接排除出业务分析 |
| `primary_key` | 源约束 PK/UK，或唯一率 ≥ 99.9% + 空值率 ≤ 1% | 系统生成（自增/UUID/无业务含义）注记 `is_surrogate=Y` |
| `foreign_key` | 源约束 FK，或 LEFT JOIN 目标表后 miss_rate ≤ 1% | 需填写 `ref_table` / `ref_column` / `join_miss_rate` |
| `business_time` | 时间类型（TIMESTAMP/DATE/DATETIME）且命名命中业务时间白名单（`*_time`、`*_at`、`*_date`，排除 `created_at` 等纯技术时间） | 填写 `time_role`（如"下单时间"） |
| `numeric_measure` | 数值类型（DECIMAL/BIGINT/INT/FLOAT/DOUBLE）且非键、非技术字段、非时间 | 下游 ④ 进一步判定可加性 |
| `low_cardinality` | `distinct_cnt ≤ 50` 且（`distinct_rate ≤ 0.5%` 或 `total_cnt < 10,000`） | 状态/枚举/标志字段，候选 Junk Dimension |
| `business_attr` | 以上均不命中的字段 | 兜底角色，包含文本描述、JSON、复杂类型等 |

角色判定优先级：`tech_meta` > `primary_key` > `foreign_key` > `business_time` > `numeric_measure` > `low_cardinality` > `business_attr`

---

## 3. 产出物

### 3.1 `dwm_inv_source_registry`（数据源注册表）

一行一个数据源。产出格式：CSV，路径 `output/dwm-bus-matrix/inventory/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| source_code | 数据源编码 | 是 | 主键，全局唯一 |
| source_type | 数据源类型 | 是 | `MySQL` / `PostgreSQL` / `API` / `CSV` / `Log` 等 |
| conn_info | 连接信息 | 是 | 连接串 / API 地址 / 文件路径 |
| charset | 字符集 | 否 | 如 `utf8mb4` |
| table_count | 表数量 | 是 | 该数据源包含的表数量 |
| status | 状态 | 是 | `active` / `inactive` / `pending` |
| has_ddl | 是否有 DDL | 是 | `Y` / `N` |
| has_constraint | 是否有约束信息 | 是 | `Y` / `N` |
| has_comment | 是否有字段注释 | 是 | `Y` / `N` |
| completeness_level | 完整度等级 | 是 | `完整` / `部分` / `缺失` |
| fallback_strategy | 降级策略 | 是 | `标准流程` / `降级流程` / `快速模式` |
| source_desc | 数据源描述 | 否 | 数据源业务说明，无信息时留空 |
| owner | 负责人 | 否 | 第二步回填 |
| registered_at | 注册时间 | 是 | 数据源登记时间 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code`

### 3.2 `dwm_inv_ods_inventory`（ODS 表清单）

一行一张 ODS 表。产出格式：CSV，路径 `output/dwm-bus-matrix/inventory/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| source_code | 数据源编码 | 是 | 关联 `dwm_inv_source_registry` |
| src_table_name | 源表名 | 是 | 源系统表名/接口名/文件名 |
| ods_table_name | ODS 表名 | 是 | 主键，目标 ODS 表名 |
| src_table_comment | 源表注释 | 否 | 源系统表注释 |
| column_count | 字段数 | 是 | 该表字段数量 |
| row_count | 行数 | 是 | 该表大致行数 |
| sync_mode | 同步模式 | 是 | `FULL` / `INCR` |
| sync_freq | 同步频率 | 是 | `T+1` / `实时` / `小时` 等 |
| partition_column | 分区字段 | 条件 | 增量时必填，如 `dt` |
| incr_column | 增量标识字段 | 条件 | `sync_mode=INCR` 时必填 |
| storage_format | 存储格式 | 是 | `ORC` / `Parquet` / `Text` 等 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`ods_table_name`

### 3.3 `dwm_inv_field_registry`（源字段清单）

一行一个源字段。产出格式：CSV，路径 `output/dwm-bus-matrix/inventory/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| source_code | 数据源编码 | 是 | 关联 `dwm_inv_source_registry` |
| src_db_name | 源库名 | 是 | API/文件类可填 source_name |
| src_table_name | 源表名 | 是 | 源系统表名 |
| src_column_name | 源字段名 | 是 | 字段英文名 |
| ordinal_position | 字段序号 | 是 | 字段在表中的顺序 |
| data_type | 数据类型 | 是 | 如 `bigint(20)`、`varchar(100)` |
| is_nullable | 是否可空 | 是 | `YES` / `NO` |
| column_default | 默认值 | 否 | 如 `NULL`、`CURRENT_TIMESTAMP` |
| column_comment | 字段注释 | 是 | 字段中文说明 |
| constraint_type | 约束类型 | 否 | `PK` / `UK` / `FK` / `INDEX` / `-` |
| ref_table | 引用表名 | 条件 | `constraint_type='FK'` 时必填 |
| ref_column | 引用字段名 | 条件 | `constraint_type='FK'` 时必填 |
| ods_table_name | ODS 表名 | 是 | 关联 `dwm_inv_ods_inventory` |
| ods_column_name | ODS 字段名 | 是 | 目标 ODS 字段名（有重命名则不同于 src_column_name） |
| transform_rule | 转换规则 | 否 | 字段重命名 / 类型转换 / 编码转换 / 无 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code + src_table_name + src_column_name`
>
> **注**：有字段重命名的必须记录 `ods_column_name` 和 `transform_rule`，避免画像时因字段名不一致误判。

### 3.4 `dwm_inv_field_profile`（字段客观画像）

一行一个字段的画像结果。产出格式：CSV，路径 `output/dwm-bus-matrix/inventory/`。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|---------|
| ods_table_name | ODS 表名 | 是 | 主键之一，关联 `dwm_inv_ods_inventory` |
| col_name | 字段名 | 是 | 主键之二，对应 `dwm_inv_field_registry.ods_column_name` |
| col_type | 字段类型 | 是 | 如 `string` / `bigint` / `decimal(18,2)` |
| col_comment | 字段注释 | 是 | 来自源库注释或人工补充 |
| field_role | 客观角色 | 是 | 7 种之一：`primary_key` / `foreign_key` / `business_time` / `tech_meta` / `numeric_measure` / `low_cardinality` / `business_attr` |
| is_numeric | 是否数值型 | 是 | `Y` / `N`（`numeric_measure` 必须为 `Y`） |
| is_surrogate | 是否代理键 | 条件 | `field_role=primary_key` 时必填：`Y`（自增/UUID）/ `N`（业务键） |
| ref_table | 外键引用表 | 条件 | `field_role=foreign_key` 时必填 |
| ref_column | 外键引用字段 | 条件 | `field_role=foreign_key` 时必填 |
| join_miss_rate | 外键 JOIN 缺失率 | 条件 | `field_role=foreign_key` 时必填，`≤ 0.01` 为有效外键 |
| time_role | 时间角色 | 条件 | `field_role=business_time` 时必填，如"下单时间"、"支付时间" |
| total_cnt | 总行数 | 是 | 画像统计窗口内总行数 |
| distinct_cnt | 去重数 | 是 | 去重计数 |
| distinct_rate | 去重率 | 是 | `distinct_cnt / total_cnt`，保留 6 位小数 |
| null_cnt | 空值数 | 是 | 空值计数 |
| null_rate | 空值率 | 是 | `null_cnt / total_cnt`，保留 6 位小数 |
| min_val | 最小值 | 否 | 转为 STRING 后的最小值 |
| max_val | 最大值 | 否 | 转为 STRING 后的最大值 |
| sample_values | 样本值 | 否 | 逗号分隔，最多 5 个典型值 |
| role_evidence | 角色判定依据 | 是 | 简述命中哪条规则（约束/唯一率/命名/JOIN） |
| profile_dt_start | 画像统计起始日期 | 是 | 如 `2024-01-01` |
| profile_dt_end | 画像统计截止日期 | 是 | 如 `2024-01-31` |
| updated_at | 更新时间 | 是 | 最近画像时间 |

> 主键：`ods_table_name + col_name`

---

## 4. 验收标准

1. **数据源覆盖率 100%**：`dwm_inv_source_registry` 中每个数据源有唯一 `source_code`
2. **元数据评估 100%**：每个数据源必须标记 `completeness_level`
3. **ODS 对象覆盖率 100%**：`dwm_inv_ods_inventory` 中每张 ODS 表有唯一命名与同步策略
4. 增量表均明确 `incr_column` 与时间边界
5. **`dwm_inv_field_registry` 覆盖率 ≥ 90%**（API/文件类可豁免部分字段）
6. 字段映射完整性 100%：有字段重命名的必须记录 `ods_column_name` 和 `transform_rule`
7. **`dwm_inv_field_profile` 覆盖率 ≥ 90%**：每个已登记字段均需完成画像（快速模式可豁免无法采样的字段，标记 `role_evidence='无法采样'`）
8. 所有 `field_role=foreign_key` 的字段已填写 `join_miss_rate`，且 ≤ 1%（超出需人工确认）
9. 本步产出物不包含主题域信息（主题域归属由 ② 管理）

---

## 5. 与下游衔接

| 下游 Skill | 消费字段 | 用途 |
|-----------|---------|------|
| ② dwm-2-business-process | `dwm_inv_field_profile.field_role` / `dwm_inv_field_registry.constraint_type` | 画表关系图，发现外键连线 |
| ② dwm-2-business-process | `dwm_inv_ods_inventory.sync_mode` | 判断表增量特征 → 事实候选依据 |
| ② dwm-2-business-process | `dwm_inv_source_registry.completeness_level` | 决定是否进入接口降级策略 |
| ③ dwm-3-dimension | `dwm_inv_field_profile WHERE field_role='foreign_key'` | 维度引用提取 |
| ③ dwm-3-dimension | `dwm_inv_field_profile WHERE field_role='low_cardinality'` | 低基数离散属性候选 |
| ④ dwm-4-fact | `dwm_inv_field_profile WHERE is_numeric='Y' AND field_role='numeric_measure'` | 度量候选池 |
| ④ dwm-4-fact | `dwm_inv_field_registry.data_type` | 字段类型信息 |
| ⑤ dwm-5-bus-matrix | `dwm_inv_field_registry.data_type` | ODS 溯源字段类型 |

---

## 6. 代码规范

### CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

### 批量画像脚本示例

当字段数量多（> 50 张表）需批量生成画像 SQL 时，use context7 获取执行引擎（HiveQL / SparkSQL / Presto）的最新语法文档，再编写批处理脚本：

```python
import sys, os
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv

# 读取字段清单
fields = read_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_registry.csv")

# 按表分组，生成画像 SQL，执行后回填 profile 结果
profiles = []
# ... 批量处理逻辑

write_csv("output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv", profiles)
```
