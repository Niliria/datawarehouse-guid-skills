# DIM 维度建模

根据统一建模上下文生成一致性维度。优先使用上游 DIM spec 的显式定义，不在模板中猜测业务属性。

## 设计步骤

1. 保留上游 `维度表名`；缺失时才生成 `dim_{entity}`。
2. 使用 `字段角色=pk/bk` 确定业务键。
3. 使用 `字段角色=attribute` 收集维度属性。
4. 使用表级 `SCD策略` 确定整体 SCD 类型。
5. 使用字段级 `SCD类型` 确定需要历史追踪的属性。
6. 保留来源 ODS 表、来源字段、字段类型和 join spec。
7. 生成代理键、DDL、ETL 和字段映射。

业务键缺失时使用 `{entity}_id` 作为兜底，并写入校验告警。不得只依赖代理键完成源系统对账。

## 字段口径

DIM 默认包含：

- `{entity}_sk`：稳定代理键
- 业务键：来自 DIM spec 的 `pk/bk`
- 维度属性：来自 `attribute`
- SCD 管理字段：按策略生成
- `etl_insert_time`、`etl_update_time`
- `pt` 分区

排除以下字段：

- `etl_*`、`_etl_*`、`_sys_*`
- `tmp_*`、`temp_*`
- 标记为废弃或 deprecated 的字段
- 与维度粒度无关的其他实体字段

## SCD 策略

### SCD Type I

用于无需历史追踪的静态或低风险属性。覆盖更新当前值，不生成 `begin_date/end_date/is_active`。

### SCD Type II

用于需要完整历史回溯的属性。生成：

- `begin_date`：版本生效日期
- `end_date`：版本失效日期，当前记录使用 `9999-12-31`
- `is_active`：当前版本为 `1`，历史版本为 `0`

保持历史代理键稳定。新增版本时生成新 SK，不得每日重排旧 SK。事实表关联时明确使用当前版本还是事件发生时版本。

### SCD Type III

用于仅保留当前值和前值的场景。生成 `prior_{attribute}` 和 `effective_date`。

### 策略优先级

1. 使用上游 `SCD策略`。
2. 使用字段级 `SCD类型`。
3. 使用明确的历史追踪需求。
4. 最后使用 `modeling.default_scd_type`。

不要仅因存在 `update_time` 就覆盖上游显式策略。日期和时间维度默认使用 Type I。

## 类型映射

| 来源类型 | 目标类型 |
|---|---|
| `TINYINT` | `TINYINT` |
| `SMALLINT` | `SMALLINT` |
| `INT/INTEGER` | `INT` |
| `BIGINT` | `BIGINT` |
| `DECIMAL/NUMERIC` | 保留精度，缺失时使用 `DECIMAL(18,2)` |
| `FLOAT/DOUBLE` | 同名目标类型 |
| `CHAR/VARCHAR/TEXT/STRING` | `STRING` |
| `DATE/DATETIME/TIME/TIMESTAMP` | 当前脚本标准化为 `STRING` |

## 设计字典

| 字段 | 说明 |
|---|---|
| `table_name` | 维度表名 |
| `entity` | 维度实体 |
| `business_key` | 业务键 |
| `business_key_source` | 来源业务键字段 |
| `business_key_type` | 业务键类型 |
| `attributes` | 维度属性 |
| `scd_type` | 表级 SCD 类型 |
| `source_tables` | 来源 ODS 表 |
| `source_joins` | ODS 关联关系 |

## 验收标准

1. 确认每个 DIM 同时存在代理键和业务键。
2. 确认非日期维度至少包含一个属性。
3. 确认代理键使用 `{entity}_sk`。
4. 确认 SCD Type II 字段完整。
5. 确认物理表名和字段名仅使用小写英文、数字和下划线。
6. 确认 DDL/ETL 不包含未渲染占位符。

## 常见反模式

- 缺少业务键：回到 DIM spec 补充 `pk/bk`。
- 混合粒度：拆分不同实体维度。
- 所有维度默认 Type II：根据历史需求重新确认。
- 日期维度使用 Type II：改为 Type I。
- 代理键每日重排：改为稳定 SK 生成策略。
- DIM 只有外键没有描述属性：补充同粒度常用属性。
