# 第二步：逐表字段打标签

在不引入新标签体系的前提下，基于 Kimball 与阿里分层实践，将每张 ODS 表的每个字段转成可计算的语义资产，直接喂给第三步（业务过程识别）和第四步（维度与事实确定）。

---

## 1. 输入

1. `dwm_s1_ods_inventory`（ODS 表清单）
2. `dwm_s1_field_registry`（源字段清单，含约束信息与 ODS 映射）
3. `dwm_s1_source_registry`（数据源注册表，含元数据完整度评估）
4. 每张 ODS 表的字段元数据（字段名、类型、注释）
5. 小样本数据（建议最近 7~30 天）

## 2. 与后续步骤的输入契约

- 第三步的 `[ID]` = `[业务键] + [代理键] + [外键]`
- 第四步的 `[度量]` = `[可加度量] + [半可加度量] + [不可加度量]`
- 第四步的 `[维度]` = `[维度属性] + [层级属性] + [SCD属性] + [退化维度] + [低基数离散属性候选]`

---

## 3. 标签体系（固定 15 个）

### 3.1 核心标签（10 个，每字段必须且只能命中 1 个）

| 标签 | 定义 | 典型字段 | 下游用途 |
|------|------|----------|----------|
| [业务键] | 源系统天然业务唯一标识 | order_no, user_code | 主表识别、主键候选 |
| [代理键] | 系统生成、无业务意义的键 | id, sk_user | 维表主键候选 |
| [外键] | 引用其他实体主键/业务键 | user_id, product_id | 第三步关系连线 |
| [退化维度] | 事实表中的交易凭证/业务单号，不单独建维表 | order_no, invoice_no | 交易追踪与明细定位 |
| [可加度量] | 可沿所有维度求和 | amount, qty | 指标聚合 |
| [维度属性] | 描述实体属性，不参与求和 | user_name, city | 维表属性 |
| [业务时间] | 业务动作发生时间 | order_time, pay_time | 过程识别、时间分析 |
| [技术时间] | 采集/同步/处理时刻 | etl_time, sync_time | 血缘审计 |
| [技术属性] | 与业务语义无关的技术元数据（非时间） | op_type, batch_id | 治理排除 |
| [低基数离散属性候选] | 低基数离散状态/枚举/标志字段 | order_status, pay_channel | Junk Dimension 候选 |

### 3.2 扩展标签（5 个，每字段可命中 0~2 个）

| 标签 | 定义 | 典型字段 | 下游用途 |
|------|------|----------|----------|
| [半可加度量] | 仅在部分维度可加（通常不可跨时间累加） | balance, inventory | 指标口径约束 |
| [不可加度量] | 不可求和，宜均值/比率/去重 | rate, unit_price | 聚合函数约束 |
| [层级属性] | 可形成上卷下钻层级 | province/city/district | 维度层级建模 |
| [SCD属性] | 可能随时间变化的维度属性 | user_level, org_name | SCD 策略判断 |
| [多值/复杂属性] | 数组、JSON、KV 等复杂结构 | tags_json, attr_map | DWD 拆解决策 |

---

## 4. 核心标签决策树

```text
入口：字段 c（表 t）
  |
  |-- Q1: c 是否属于技术元数据域？(源映射标注为ETL字段，或命中技术白名单)
  |      |-- YES:
  |      |     |-- Q1.1: c 是否为处理链路时间？(etl/sync/load/op_ts/insert_time)
  |      |           |-- YES -> [技术时间] -> STOP
  |      |           |-- NO  -> [技术属性] -> STOP
  |      |
  |      |-- NO:
  |            |-- Q2: c 是否为键候选？(命中PK/UK/FK/索引或命名为*_id/*_no/*_code)
  |                 |-- YES:
  |                 |     |-- Q2.1: 源约束是否指向 PK/UK？
  |                 |     |     |-- YES:
  |                 |     |     |     |-- Q2.1.1: 是否系统生成？(自增/序列/UUID/无业务语义)
  |                 |     |     |           |-- YES -> [代理键] -> STOP
  |                 |     |     |           |-- NO  -> [业务键] -> STOP
  |                 |     |     |
  |                 |     |     |-- NO:
  |                 |     |           |-- Q2.2: 是否满足外键阈值？(join miss_rate <= 1%)
  |                 |     |                 |-- YES -> [外键] -> STOP
  |                 |     |                 |-- NO:
  |                 |     |                      |-- Q2.3: 是否满足业务键阈值？
  |                 |     |                           (唯一率>=99.9%, 空值率<=1%, 格式一致率>=95%)
  |                 |     |                           |-- YES -> [业务键](待确认) -> STOP
  |                 |     |                           |-- NO  -> 进入 Q3
  |                 |
  |                 |-- NO -> 进入 Q3
  |
  |-- Q3: c 是否为业务发生时间？(创建/支付/发货/退款等业务动作时刻)
  |      |-- YES -> [业务时间] -> STOP
  |      |-- NO:
  |            |-- Q3.1: c 是否为技术处理时间？
  |                  |-- YES -> [技术时间] -> STOP
  |                  |-- NO  -> 进入 Q4
  |
  |-- Q4: c 是否数值型可用于度量？(numeric/decimal/bigint 且有业务度量语义)
  |      |-- YES:
  |      |     |-- Q4.1: 可跨时间安全求和？
  |      |     |      |-- YES -> [可加度量] -> STOP
  |      |     |      |-- NO:
  |      |     |           |-- Q4.2: 可跨非时间维求和但不可跨时间？
  |      |     |                 |-- YES -> [半可加度量] -> STOP
  |      |     |                 |-- NO  -> [不可加度量] -> STOP
  |      |
  |      |-- NO -> 进入 Q5
  |
  |-- Q5: c 是否交易凭证/业务单号且位于事实候选表？
  |      [注：Q5 依赖 fact_candidate 初判结果，属于第二遍扫描执行]
  |      |-- YES -> [退化维度] -> STOP
  |      |-- NO  -> 进入 Q6
  |
  |-- Q6: c 是否低基数离散字段？(distinct_cnt<=50 且 (distinct_rate<=0.5% 或 total_count<10000))
  |      |-- YES -> [低基数离散属性候选] -> STOP
  |      |-- NO  -> 进入 Q7
  |
  |-- Q7: c 是否可形成层级？(省/市/区, 一级类目/二级类目)
  |      |-- YES -> [维度属性] + 扩展[层级属性] -> STOP
  |      |-- NO:
  |            |-- Q7.1: c 是否多值或复杂结构？(array/map/struct/json)
  |                 |-- YES -> [维度属性] + 扩展[多值/复杂属性] -> STOP
  |                 |-- NO  -> [维度属性] -> STOP
```

### 冲突裁决规则

1. `[技术属性]/[技术时间]` > 所有业务标签
2. `[代理键]` > `[业务键]`（同字段不可同时成立）
3. `[外键]` 与 `[业务键]` 冲突时：当前表是主实体表 → `[业务键]`；当前表是引用表 → `[外键]`
4. `[退化维度]` 仅适用于事实候选表；若在实体主表出现同字段 → `[业务键]`
5. 状态/渠道/标志一律不判 `[退化维度]` → 优先 `[低基数离散属性候选]`

### 扩展标签决策（核心标签之后执行）

1. 核心为 `[维度属性]` 且可构成父子层级 → 追加 `[层级属性]`
2. 核心为 `[维度属性]` 且有历史变化分析需求 → 追加 `[SCD属性]`
3. 核心为度量类 → 补充 `agg_suggest`
4. 字段为 array/json/map/struct → 追加 `[多值/复杂属性]`，标注 `complex_type`

---

## 5. 判定阈值

| 指标 | 阈值 | 适用标签 |
|------|------|----------|
| 唯一率 `distinct_cnt/total` | >= 99.9% | [业务键] 候选 |
| 空值率 `null_cnt/total` | <= 1% | [业务键]/[外键] 候选 |
| 外键缺失率 `miss_cnt/ref_cnt` | <= 1% | [外键] |
| 低基数上限 `distinct_cnt` | <= 50 | [低基数离散属性候选] |
| 低基数占比 `distinct_cnt/total` | <= 0.5%（`total_count < 10000` 时豁免） | [低基数离散属性候选] |

> 阈值可按行业调整，但须在项目级"标注参数表"中统一，不允许按人临时修改。

### 校验 SQL 模板

```sql
-- A. 唯一率/空值率（业务键候选）
SELECT
  COUNT(*) AS total_cnt,
  COUNT(DISTINCT candidate_key) AS distinct_cnt,
  SUM(CASE WHEN candidate_key IS NULL THEN 1 ELSE 0 END) AS null_cnt
FROM ods_xxx
WHERE dt BETWEEN '${start_dt}' AND '${end_dt}';

-- B. 外键缺失率（外键候选）
SELECT
  COUNT(1) AS ref_cnt,
  SUM(CASE WHEN d.user_id IS NULL THEN 1 ELSE 0 END) AS miss_cnt
FROM ods_fact f
LEFT JOIN ods_user d ON f.user_id = d.user_id
WHERE f.user_id IS NOT NULL
  AND f.dt BETWEEN '${start_dt}' AND '${end_dt}';

-- C. 低基数判定
SELECT
  COUNT(*) AS total_cnt,
  COUNT(DISTINCT status_code) AS distinct_cnt
FROM ods_xxx
WHERE dt BETWEEN '${start_dt}' AND '${end_dt}';
```

### 置信度评分

| 分值 | 规则 | 置信度 |
|------|------|--------|
| >= 8 | 源约束 + 映射 + 画像全部通过 | 高 |
| 5~7 | 无源约束，但画像阈值通过且文档支持 | 中 |
| <= 4 | 仅命名推断或证据冲突 | 低（必须业务确认） |

计分：源约束 4 分，映射 2 分，画像 2 分，命名 1 分。

---

## 6. 证据链与优先级

**标准模式（元数据完整）：**
1. 源系统约束（PK/UK/FK/索引）与数据字典 — 强证据
2. 源到 ODS 字段映射 — 强证据
3. Hive ODS 数据画像 — 验证证据
4. 字段命名规则 — 弱证据（不可单独定核心标签）

**降级模式（元数据部分缺失）：**
1. Hive ODS 数据画像（提升为主证据）
2. 字段命名 + 业务文档
3. 业务访谈（仅核心表关键字段）

**快速模式（元数据严重缺失）：**
1. 仅标注确定性字段：技术属性/技术时间、明显度量（amount/qty）、明显时间（*_time）
2. 其余统一标记 `[维度属性](待确认)`
3. 第三步通过 JOIN 反推外键，第四步通过聚合反推事实表粒度

---

## 7. 执行流程（两遍扫描）

**第一遍（Q1~Q4 + Q6~Q7，跳过 Q5）：**

1. 拉取源系统证据：PK/UK/FK/索引、字段注释、源到 ODS 字段映射
2. 读取 ODS 元数据：字段名（使用 `ods_column_name`，非源系统字段名；有重命名的通过 `transform_rule` 确认映射）、类型、注释、样本值
3. 预标注：按命名规则给初始标签
4. 技术类剔除：定 [技术属性]/[技术时间]（Q1）
5. 键类确认：定 [业务键]/[代理键]/[外键]（Q2）
6. 时间与度量确认：定 [业务时间] 与度量三分法（Q3~Q4）
7. 属性类收敛：定 [低基数离散属性候选]/[维度属性]/[层级属性]/[SCD属性]/[多值/复杂属性]（Q6~Q7）。交易凭证类字段暂标 [维度属性]

**fact_candidate 初判（表级，批次内统一执行）：**

8. 按 §8 规则，基于标签统计判定每张表的 `fact_candidate`

**第二遍（仅 Q5，针对 fact_candidate=Y 的表）：**

9. 对 `fact_candidate=Y(初判)` 的表，将符合退化维度条件的字段从 [维度属性] 修正为 [退化维度]

**收尾：**

10. 低置信度回合：输出业务确认清单并回填最终标签
11. 质量门禁：通过后进入第三步

---

## 8. fact_candidate 初判规则

> 消除循环依赖：本步需输出 `fact_candidate`，但正式识别在第三步。此处定义初判规则，第三步可修正。

### 初判条件（满足任一标 `Y`）

| 条件 | 说明 |
|------|------|
| 外键数 >= 2 且度量字段数 >= 1 | 引用多个实体 + 有可聚合数值 |
| 存在业务时间 + 行数远大于引用实体表 | 流水型行为记录 |
| sync_mode = INCR 且有明确增量时间字段 | 持续增长的流水表 |

### 注意事项

1. 初判结果标记为 `fact_candidate=Y(初判)`，与第三步 `Y(确认)` 区分
2. 仅有外键但无度量、无业务时间 → 标记 `N`
3. 中间表（既有业务键又有外键+度量）→ 标记 `Y(初判)`，第三步通过关系图确认
4. `fact_candidate` 为表级属性，同表所有字段行值必须一致

---

## 9. 产出物：`dwm_s2_field_tag`

一行一个字段，扁平结构。产出格式：数据库表 / CSV。

> **元数据权威源**：`col_type`/`col_comm` 等基础元数据与 `dwm_s1_field_registry` 存在冗余，以支持扁平查询。权威源为 `dwm_s1_field_registry`，变更时须同步更新。

### 字段定义

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
| src_db_name | 源库名 | 是 | API/CSV 可填 source_name |
| src_table_name | 源表名 | 是 | 源系统表名 |
| ods_table_name | ODS 表名 | 是 | 联合主键之一 |
| col_name | 字段英文名 | 是 | 联合主键之二，对应 `dwm_s1_field_registry.ods_column_name`（非源系统字段名） |
| col_type | 字段类型 | 是 | 如 `string`/`bigint`/`decimal(18,2)` |
| col_comm | 字段中文注释 | 是 | 来自源库注释或人工补充 |
| core_tag | 核心标签 | 是 | 10 个核心标签之一 |
| ext_tags | 扩展标签 | 否 | 逗号分隔，无值时留空 |
| ref_table | 引用表名 | 条件 | `core_tag=外键` 时必填 |
| ref_column | 引用字段名 | 条件 | `core_tag=外键` 时必填 |
| join_miss_rate | 外键 JOIN 缺失率 | 条件 | `core_tag=外键` 时必填 |
| agg_suggest | 聚合建议 | 条件 | 度量标签时必填：`sum/avg/max/min/count_distinct` |
| unit | 度量单位 | 条件 | 度量标签时必填：元/件/%/次等 |
| time_role | 时间角色 | 条件 | 时间标签时必填，如"下单时间""同步时间" |
| scd_type | SCD 类型建议 | 否 | `SCD1/SCD2/SCD3` 或空 |
| complex_type | 复杂类型 | 条件 | `ext_tags` 含 `[多值/复杂属性]` 时必填：`JSON/Array/Struct/Map` |
| fact_candidate | 事实候选标记 | 是 | `Y(初判)/N`。**表级属性**，同表所有行必须一致 |
| evidence_score | 证据评分 | 是 | 0~9 |
| confidence | 置信度 | 是 | 高/中/低 |
| review_status | 审核状态 | 是 | `approved/pending/rejected` |
| reason | 判定依据说明 | 是 | 简述证据链与阈值结果 |
| updated_at | 更新时间 | 是 | 最近标注/修改时间 |

> 主键：`ods_table_name + col_name`

### 必填约束

1. 每行必填：`source_code/ods_table_name/col_name/col_type/col_comm/core_tag/fact_candidate/evidence_score/confidence/review_status/reason/updated_at`
2. `core_tag='外键'` → `ref_table/ref_column/join_miss_rate` 必填
3. `core_tag in ('可加度量','半可加度量','不可加度量')` → `agg_suggest/unit` 必填
4. `core_tag in ('业务时间','技术时间')` → `time_role` 必填
5. `ext_tags LIKE '%多值/复杂属性%'` → `complex_type` 必填
6. `fact_candidate` 一致性：`SELECT ods_table_name, COUNT(DISTINCT fact_candidate) FROM dwm_s2_field_tag GROUP BY ods_table_name HAVING COUNT(DISTINCT fact_candidate) > 1` 结果必须为空

---

## 10. 质量门禁（进入第三步前）

> 支持分批执行：按批次通过门禁即可进入后续步骤。

### 门禁检查项

1. 当批次字段标注覆盖率 = 100%（每字段都有核心标签）
2. `review_status=approved` 占比 = 100%（低置信度须闭环确认）
3. 所有 `[外键]` 满足 `join_miss_rate <= 1%`
4. 所有 `[业务键]` 满足：唯一率 >= 99.9% 且空值率 <= 1%
5. 所有度量字段已填写 `agg_suggest` 与 `unit`
6. 每张业务过程候选表至少 1 个 `[业务时间]`
7. 每张表已填写 `fact_candidate` 且同表行值一致
8. 所有 `[多值/复杂属性]` 已标注 `complex_type`

### 业务确认 SLA

| 确认类型 | 响应时限 | 超时处理 |
|---------|---------|---------|
| 核心表关键字段 | 3 工作日 | 升级至数据负责人 |
| 非核心表/字段 | 5 工作日 | 按画像结果落地，标记 `pending(超时)` |
| 主题域归属争议 | 3 工作日 | 暂归"待定域"，不阻塞后续步骤 |

---

## 11. 给下游步骤的数据包

### 给第三步

1. `WHERE core_tag IN ('业务键','代理键','外键')` → ID 清单
2. `WHERE core_tag='外键' AND ref_table IS NOT NULL` → 外键关系清单（含 `join_miss_rate`）
3. `fact_candidate='N' AND core_tag='业务键'` → 主表候选

### 给第四步

1. `WHERE core_tag IN ('可加度量','半可加度量','不可加度量')` → 度量清单
2. `WHERE core_tag='业务时间'` → 业务时间清单（含 `time_role`）
3. `WHERE fact_candidate LIKE 'Y%'` → 事实候选表（初判；第三步通过 `fact_candidate_final` 确认后，第四步以 `dwm_s3_table_profile.table_role='fact'` 为准）
4. `WHERE ext_tags LIKE '%多值/复杂属性%'` → 复杂属性清单

---

## 12. 常见误判与纠偏

1. 把 `id` 一律当 [业务键] → 先判断是否系统生成，系统生成优先 [代理键]
2. 把 `create_time` 一律当 [技术时间] → 若描述业务动作发生，判 [业务时间]
3. 把 `rate`/`price` 当 [可加度量] → 通常是 [不可加度量]
4. 把所有状态字段都拆维表 → 低基数字段优先 [低基数离散属性候选]
5. 仅凭同名字段判外键 → 必须补 `ref_table/ref_column/join_miss_rate/confidence`
