# 第一步：数据源接入与 ODS 盘点

完成"有哪些数据源"和"源里有哪些表/字段"的调研，形成字段标注的输入基座。

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

1. 按"一个独立来源一行"建立 `dwm_s1_source_registry`
2. 填写技术属性：`source_code` / `source_type` / `conn_info` / `charset` / `table_count` / `status` / `registered_at`
3. 评估元数据完整度：`has_ddl` / `has_constraint` / `has_comment` / `completeness_level` / `fallback_strategy`
4. 业务属性暂留空：`subject_area_code`（跨域数据源留空）/ `owner`（第三步回填）；`source_desc` 已知时直接填写
5. 校验唯一性：`source_code` 全局唯一

### 2.2 ODS 表盘点

1. 按数据源类型采集对象清单（数据库查元数据；API/文件人工梳理）
2. 生成 `dwm_s1_ods_inventory`
3. 判断同步方式：优先全量，满足增量边界且收益显著再用增量
4. 标准化分区策略：T+1 表统一 `dt` 分区

### 2.3 源系统元数据采集

为第二步字段标注提供"证据链"的最高优先级输入。

#### 采集内容

1. **表结构定义**：DDL 语句或 CREATE TABLE 脚本
2. **约束信息**：主键(PK)、唯一键(UK)、外键(FK)、索引(INDEX)
3. **字段注释**：COMMENT / DESCRIPTION / 接口文档说明
4. **字段属性**：数据类型、是否可空、默认值、字符集

#### 采集方式

| 数据源类型 | 采集方式 | 输出格式 |
|-----------|---------|---------|
| MySQL | `SHOW CREATE TABLE` / `information_schema.KEY_COLUMN_USAGE` | DDL + 约束清单 |
| PostgreSQL | `pg_dump --schema-only` / `pg_constraint` | DDL + 约束清单 |
| Oracle | `DBMS_METADATA.GET_DDL` / `USER_CONSTRAINTS` | DDL + 约束清单 |
| SQL Server | `sp_help` / `sys.foreign_keys` | DDL + 约束清单 |
| API 接口 | 接口文档 / Swagger / 字段说明 | 字段清单 |
| CSV/日志文件 | 文件头 / 数据字典 / 业务文档 | 字段清单 |

#### 元数据缺失应对

| 完整度等级 | 判定条件 | 第二步策略 |
|-----------|---------|-----------|
| 完整 | DDL + 约束 + 注释齐全 | 标准流程（源约束优先） |
| 部分 | 有 DDL，无约束或注释不全 | 降级流程（画像 + 命名） |
| 缺失 | 仅表名，无结构信息 | 快速模式（仅确定性字段） |

缺失时的补救措施：
1. 联系源系统 DBA/开发获取文档
2. 通过 ODS 数据反推（唯一率/外键缺失率）
3. 业务访谈（仅核心表关键字段）
4. 标记"待补充"，不阻塞后续流程

---

## 3. 产出物

### 3.1 `dwm_s1_source_registry`（数据源注册表）

一行一个数据源。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
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
| subject_area_code | 主题域编码 | 否 | 第三步回填，仅当数据源属单一主题域时填写（跨多主题域留空，以 ods_inventory 表级为准）。外键引用 `dwm_s3_subject_area` |
| source_desc | 数据源描述 | 否 | 数据源业务说明（第一步填写，无信息时留空） |
| owner | 负责人 | 否 | 第三步回填 |
| registered_at | 注册时间 | 是 | 数据源登记时间 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code`

### 3.2 `dwm_s1_ods_inventory`（ODS 表清单）

一行一张 ODS 表。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
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
| subject_area_code | 主题域编码 | 否 | 第三步回填，外键引用 `dwm_s3_subject_area` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`ods_table_name`

### 3.3 `dwm_s1_field_registry`（源字段清单）

一行一个源字段。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
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
| ods_table_name | ODS 表名 | 是 | 关联 `dwm_s1_ods_inventory` |
| ods_column_name | ODS 字段名 | 是 | 目标 ODS 字段名 |
| transform_rule | 转换规则 | 否 | 字段重命名 / 类型转换 / 编码转换 / 无 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`source_code + src_table_name + src_column_name`
>
> **注**：有字段重命名的必须记录 `ods_column_name` 和 `transform_rule`，避免第二步标注时因字段名不一致导致误判。

---

## 4. 验收标准

1. **数据源覆盖率 100%**：`dwm_s1_source_registry` 中每个数据源有唯一 `source_code`
2. **元数据评估 100%**：每个数据源必须标记 `completeness_level`
3. **ODS 对象覆盖率 100%**：`dwm_s1_ods_inventory` 中每张 ODS 表有唯一命名与同步策略
4. 增量表均明确 `incr_column` 与时间边界
5. **`dwm_s1_field_registry` 覆盖率 >= 90%**（API/文件类可豁免部分字段）
6. 字段映射完整性 100%：有字段重命名的必须记录 `ods_column_name` 和 `transform_rule`
7. 数据源注册表不混入表级字段（`subject_area_code` 待第三步回填）

---

## 5. 与下一步衔接

- `dwm_s1_ods_inventory` 的 `ods_table_name` 与字段元数据 → 第二步逐字段打标签的输入
- `dwm_s1_field_registry` 的约束信息（PK/UK/FK）→ 第二步"证据链"最高优先级输入
- `dwm_s1_field_registry` 的 `ods_column_name` / `transform_rule` → 确保第二步标注不因字段重命名误判
- `dwm_s1_source_registry` 的 `completeness_level` → 决定第二步采用标准/降级/快速模式
- `completeness_level='缺失'` 的数据源 → 第二步标记为"待确认"，第三步通过画像补充验证
