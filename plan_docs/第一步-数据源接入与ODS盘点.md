# 第一步：数据源接入与 ODS 盘点

> 目标：一次调研完成"有哪些数据源"和"源里有哪些表"，形成字段标注的输入基座。

---

## 1. 输入

| 输入项 | 说明 | 格式 |
|--------|------|------|
| 系统接入清单 | 数据库/接口/文件等数据源清单 | 文档 / 电子表格 |
| 连接参数与访问凭证 | 数据库连接串、API token、文件路径等 | 安全存储 |
| 基础网络与权限信息 | 网络白名单、访问权限配置 | 安全存储 |
| 目标 ODS 命名规则 | 数据库/表/字段命名规范 | 文档 |

---

## 2. 实施步骤

### 2.1 数据源登记

1. 按"一个独立来源一行"建立数据源注册表。
2. 填写技术属性：`source_code/source_type/conn_info/charset/table_count/status/registered_at`。
3. 业务属性暂留空：`subject_area/source_desc/owner`（后续回填）。
4. 校验唯一性：`source_code` 全局唯一。

### 2.2 ODS 表盘点

1. 按数据源类型采集对象清单：数据库查元数据；API/文件人工梳理。
2. 生成 `ODS表清单`：`source_code/src_table_name/ods_table_name/src_table_comment/column_count/row_count`。
3. 生成 `ODS同步任务台账`：`task_type/sync_mode/sync_freq/partition_column/incr_column/storage_format/hdfs_path`。
4. 判断同步方式：优先全量，满足增量边界且收益显著再用增量。
5. 标准化分区策略：T+1 表统一 `dt` 分区。

### 2.3 源系统元数据采集

> 目标：为第二步字段标注提供"证据链"的最高优先级输入。

#### 2.3.1 采集内容

1. **表结构定义**：DDL 语句或 CREATE TABLE 脚本
2. **约束信息**：主键(PK)、唯一键(UK)、外键(FK)、索引(INDEX)
3. **字段注释**：COMMENT / DESCRIPTION / 接口文档说明
4. **字段属性**：数据类型、是否可空、默认值、字符集

#### 2.3.2 采集方式（按数据源类型）

| 数据源类型 | 采集方式 | 输出格式 |
|-----------|---------|---------|
| MySQL | `SHOW CREATE TABLE` / `information_schema.KEY_COLUMN_USAGE` | DDL + 约束清单 |
| PostgreSQL | `pg_dump --schema-only` / `pg_constraint` | DDL + 约束清单 |
| Oracle | `DBMS_METADATA.GET_DDL` / `USER_CONSTRAINTS` | DDL + 约束清单 |
| SQL Server | `sp_help` / `sys.foreign_keys` | DDL + 约束清单 |
| API 接口 | 接口文档 / Swagger / 字段说明 | 字段映射表 |
| CSV/日志文件 | 文件头 / 数据字典 / 业务文档 | 字段映射表 |

#### 2.3.3 产出物

**A. 源字段清单** (`source_field_registry`)

> 一行一个源字段。记录源系统的字段定义与约束信息。
>
> **产出格式：数据库表 / CSV（格式规范详见总线矩阵构建指南）**

#### 字段定义

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联数据源注册表 |
| src_db_name | 源库名 | 是 | 数据库名，API/文件类可填 source_name |
| src_table_name | 源表名 | 是 | 源系统表名/接口名/文件名 |
| src_column_name | 源字段名 | 是 | 字段英文名 |
| ordinal_position | 字段序号 | 是 | 字段在表中的顺序 |
| data_type | 数据类型 | 是 | 如 `bigint(20)`、`varchar(100)` |
| is_nullable | 是否可空 | 是 | `YES` / `NO` |
| column_default | 默认值 | 否 | 默认值，如 `NULL`、`CURRENT_TIMESTAMP` |
| column_comment | 字段注释 | 是 | 字段中文说明 |
| constraint_type | 约束类型 | 否 | `PK` / `UK` / `FK` / `INDEX` / `-`（无约束） |
| ref_table | 引用表名 | 条件 | `constraint_type='FK'` 时必填 |
| ref_column | 引用字段名 | 条件 | `constraint_type='FK'` 时必填 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code + src_table_name + src_column_name`

#### 示例数据

| source_code | src_db_name | src_table_name | src_column_name | data_type | is_nullable | column_comment | constraint_type | ref_table | ref_column |
|---|---|---|---|---|---|---|---|---|---|
| my001 | mall_trade | order | order_id | bigint(20) | NO | 订单主键 | PK | - | - |
| my001 | mall_trade | order | user_id | varchar(50) | NO | 用户ID | FK | user | user_id |
| my001 | mall_trade | order | create_time | datetime | NO | 创建时间 | INDEX | - | - |

---

**B. 字段映射表** (`source_to_ods_mapping`)

> 一行一条映射关系。记录源字段到 ODS 字段的重命名与转换规则。
>
> **产出格式：数据库表 / CSV（格式规范详见总线矩阵构建指南）**

#### 字段定义

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联数据源注册表 |
| src_db_name | 源库名 | 是 | 数据库名 |
| src_table_name | 源表名 | 是 | 源系统表名 |
| src_column_name | 源字段名 | 是 | 源字段英文名 |
| ods_table_name | ODS表名 | 是 | 目标 ODS 表名 |
| ods_column_name | ODS字段名 | 是 | 目标 ODS 字段名 |
| transform_rule | 转换规则 | 否 | 字段重命名 / 类型转换 / 编码转换 / 无 |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code + src_table_name + src_column_name`

#### 示例数据

| source_code | src_db_name | src_table_name | src_column_name | ods_table_name | ods_column_name | transform_rule |
|---|---|---|---|---|---|---|
| my001 | mall_trade | order | create_time | my001_order | gmt_create | 字段重命名（create_time → gmt_create） |
| my001 | mall_trade | user | user_name | my001_user | name | 字段重命名（user_name → name） |
| my001 | mall_trade | order | total_amount | my001_order | total_amount | 无 |

> 第 1、2 行：字段重命名需记录，避免第二步标注时因字段名不一致导致误判。

---

**C. 元数据完整度评估** (`metadata_completeness`)

> 一行一个数据源。评估元数据完整性并标记降级策略。
>
> **产出格式：数据库表 / CSV（格式规范详见总线矩阵构建指南）**

#### 字段定义

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联数据源注册表 |
| src_db_name | 源库名 | 是 | 数据库名或 API 名称 |
| has_ddl | 是否有 DDL | 是 | `Y` / `N` |
| has_constraint | 是否有约束信息 | 是 | `Y` / `N` |
| has_comment | 是否有字段注释 | 是 | `Y` / `N` |
| completeness_level | 完整度等级 | 是 | `完整` / `部分` / `缺失` |
| fallback_strategy | 降级策略 | 是 | `标准流程` / `降级流程` / `快速模式` |
| remark | 备注 | 否 | 额外说明 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code`

#### 示例数据

| source_code | src_db_name | has_ddl | has_constraint | has_comment | completeness_level | fallback_strategy |
|---|---|---|---|---|---|---|
| my001 | mall_trade | Y | Y | Y | 完整 | 标准流程（源约束优先） |
| api001 | payment_api | Y | N | Y | 部分 | 降级流程（画像+命名） |
| log001 | access_log | N | N | N | 缺失 | 快速模式（仅确定性字段） |

---

#### 2.3.4 元数据缺失应对策略

| 完整度等级 | 判定条件 | 第二步策略 | 优先级 |
|-----------|---------|-----------|:--:|
| 完整 | DDL + 约束 + 注释齐全 | 标准流程（源约束优先） | P0 |
| 部分 | 有DDL，无约束或注释不全 | 降级流程（画像+命名） | P1 |
| 缺失 | 仅表名，无结构信息 | 快速模式（仅确定性字段） | P2 |

**缺失时的补救措施：**
1. 联系源系统DBA/开发获取文档
2. 通过ODS数据反推（唯一率/外键缺失率）
3. 业务访谈（仅核心表关键字段）
4. 标记"待补充"，不阻塞后续流程

---

## 3. 输出

> 产出整合为 **6 张结构化表 + 1 份文档**。所有表输出格式详见总线矩阵构建指南 §8。

| 输出项 | 说明 | 格式 | 必要性 |
|--------|------|------|:--:|
| `数据源注册表` | 数据源清单与技术属性 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需 |
| `ODS表清单` | 所有 ODS 表清单与同步策略 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需 |
| `ODS同步任务台账` | 同步任务配置信息 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需 |
| `source_field_registry` | 源字段定义与约束信息 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需 |
| `source_to_ods_mapping` | 源字段到 ODS 字段映射 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需（有重命名时） |
| `metadata_completeness` | 元数据完整度评估 | 数据库表 / CSV（格式规范详见总线矩阵构建指南） | 必需 |
| `待回填字段清单` | 业务描述、负责人等待补充字段 | 文档 / 表格 | 按需 |

---

## 4. 验收标准

1. **数据源覆盖率 100%**：每个数据源有唯一 `source_code`
2. **ODS 对象覆盖率 100%**：每张 ODS 表有唯一命名与同步策略
3. **增量表均明确 `incr_column` 与时间边界**
4. **数据源注册表不混入表级字段**（如 `subject_area`）
5. **`source_field_registry` 覆盖率 >= 90%**（API/文件类可豁免部分字段）
6. **`source_to_ods_mapping` 完整性 100%**（有字段重命名的必须记录）
7. **`metadata_completeness` 评估 100%**（每个数据源必须标记完整度等级）

---

## 5. 与下一步衔接

- `ods_table_name` 与字段元数据，作为第二步逐字段打标签的输入。
- `source_field_registry` 中的约束信息（PK/UK/FK），作为第二步"证据链"的最高优先级输入。
- `source_to_ods_mapping` 确保第二步标注时不会因字段重命名导致误判。
- `metadata_completeness` 决定第二步采用标准流程还是降级流程。
- `completeness_level='缺失'` 的数据源，需在第二步快速模式中标记为"待确认"，并在第三步通过数据画像补充验证。
