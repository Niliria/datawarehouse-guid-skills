# 第三步：业务过程识别与粒度声明

通过表关系网识别业务过程（总线矩阵的行），同步声明每个过程的粒度——不声明粒度的业务过程识别没有意义。

---

## 1. 输入

从 `dwm_s2_field_tag` 按条件过滤获取：

| 过滤条件 | 产出 | 用途 |
|---------|------|------|
| `core_tag IN ('业务键','代理键','外键')` | ID 清单 | 画表关系图 |
| `core_tag='外键' AND ref_table IS NOT NULL` | 外键关系清单（含 `join_miss_rate`） | 连线主依据 |
| `fact_candidate='N' AND core_tag='业务键'` | 主表候选 | 维度候选池 |
| `core_tag IN ('可加度量','半可加度量','不可加度量')` | 度量清单 | 业务过程判定 |
| `core_tag='业务时间'` | 业务时间清单 | 业务过程判定 |

### 接口数据无主键降级策略

接口数据（API/文件/消息队列）通常无 PK/FK 约束，第二步证据链上限仅 5 分。在本步骤通过数据画像补充证据。

| 场景 | 降级处理 | 操作方法 |
|------|---------|---------| 
| 无主键 | 画像发现天然业务键 | 候选列唯一率 >= 99.9% + 空值率 <= 1% → 业务键候选 |
| 无外键约束 | JOIN 命中率发现关系 | 候选字段 LEFT JOIN 目标表，`miss_rate <= 1%` → 外键候选 |
| 联合键才唯一 | 逐步增加组合字段 | 找满足唯一性的最小字段集 → 粒度键 |
| 同名字段无约束 | 值域匹配作弱证据 | 类型一致 + 值域重叠度 > 95% → 候选关系，需人工确认 |

**回写要求**：画像发现的业务键/外键须回写 `dwm_s2_field_tag` 的 `core_tag`、`ref_table`、`ref_column`、`join_miss_rate`、`evidence_score`、`confidence`。

```sql
-- 唯一率分析（发现天然业务键）
SELECT COUNT(*) AS total,
       COUNT(DISTINCT candidate_col) AS distinct_cnt,
       SUM(CASE WHEN candidate_col IS NULL THEN 1 ELSE 0 END) AS null_cnt
FROM ods_xxx;

-- JOIN 命中率分析（发现外键关系）
SELECT COUNT(1) AS ref_cnt,
       SUM(CASE WHEN b.target_col IS NULL THEN 1 ELSE 0 END) AS miss_cnt,
       ROUND(SUM(CASE WHEN b.target_col IS NULL THEN 1 ELSE 0 END) / COUNT(1), 4) AS miss_rate
FROM ods_source a
LEFT JOIN ods_target b ON a.source_col = b.target_col
WHERE a.source_col IS NOT NULL;
```

---

## 2. 实施步骤

### 2.1 画表关系图（手段，非独立交付）

1. 以 `dwm_s2_field_tag WHERE core_tag='外键'` 为主线画连线（不是仅靠同名字段）
2. 对同名 ID 做补充候选，再做语义核验（实体含义、值域、JOIN 命中率）
3. 区分角色：
   - 主表：被引用为主、实体属性稳定（维度候选）
   - 引用表：引用多个实体且承载行为（事实候选）
4. 接口数据补充：对第二步标记为 `待确认` 的外键字段，通过实际 JOIN 验证后确认或排除，回写 `dwm_s2_field_tag`
5. 产出结果写入 `dwm_s3_table_profile`

### 2.2 识别业务过程并归组主题域

1. 逐表按四类证据评估：时间证据、度量证据、关联证据、增长证据
2. 判定结果：`fact` / `dimension` / `config` / `exclude`
   - `config`：系统配置/参数表，非业务实体（如枚举映射、系统参数、开关配置），不参与维度建模，建设阶段按需同步到 DIM 层或作为码表引用
3. 无数值但有行为轨迹的表 → `table_role=fact`，在 `role_evidence` 中注明 factless
4. 形成标准命名：如下单、支付、退款、浏览
5. **主题域定义与归组**：
   - 先定义主题域 → 产出 `dwm_s3_subject_area`
   - 定义方法：先自底向上（按业务过程的实体关系自然聚类），再自顶向下（对照企业价值链校验）
   - 每个主题域必须有：中文名、英文名、编码（2~3 大写字母）、描述
   - 再归组：将业务过程归入已定义的主题域（通过 `subject_area_code` 外键）
   - 约束：一个业务过程只能归属一个主题域
6. 回填第一步：`dwm_s1_ods_inventory` 的 `subject_area_code`（必填）；`dwm_s1_source_registry` 的 `subject_area_code` 仅当数据源属单一主题域时回填（跨多主题域的数据源留空，以表级 ods_inventory 为准）

### 2.3 声明粒度

1. 按业务过程写一句话粒度声明（例：一行一笔支付交易）
2. 识别承载粒度的键：主键或联合键
3. 做唯一性校验：`COUNT(*)` 对比 `COUNT(DISTINCT 粒度键)`
4. 若不唯一 → 回退修正：补联合键或下钻到更细明细层
5. 接口数据无主键时：通过 §1 唯一率分析发现天然键或联合键作为粒度键

---

## 3. 产出物

### 3.1 `dwm_s3_table_profile`（表角色画像表）

一行一张表。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| source_code | 数据源编码 | 是 | 关联 `dwm_s1_source_registry` |
| ods_table_name | ODS 表名 | 是 | 主键 |
| table_role | 表角色 | 是 | `fact` / `dimension` / `config` / `exclude` |
| role_evidence | 角色判定依据 | 是 | 四类证据综合说明 |
| business_process | 业务过程名称 | 条件 | `table_role=fact` 时必填 |
| bp_standard_name | 业务过程标准命名 | 条件 | `table_role=fact` 时必填 |
| bp_desc | 业务过程描述 | 条件 | `table_role=fact` 时必填 |
| subject_area_code | 主题域编码 | 条件 | `table_role != 'exclude'` 时必填，外键引用 `dwm_s3_subject_area` |
| subject_area_basis | 主题域归组依据 | 条件 | `table_role != 'exclude'` 时必填 |
| fact_type | 事实表类型 | 条件 | 第四步回写：`transaction` / `periodic_snapshot` / `accumulating_snapshot` / `factless` |
| fact_type_evidence | 事实表类型判定依据 | 条件 | 第四步回写 |
| grain_statement | 粒度声明 | 条件 | `table_role IN (fact, dimension)` 时必填 |
| grain_keys | 粒度键 | 条件 | `table_role IN (fact, dimension)` 时必填 |
| grain_total_count | 校验-总行数 | 条件 | `COUNT(*)` 结果 |
| grain_distinct_count | 校验-去重数 | 条件 | `COUNT(DISTINCT 粒度键)` 结果 |
| grain_check_result | 校验结果 | 条件 | `pass` / `fail` |
| fact_candidate_final | 事实候选最终判定 | 是 | `Y(确认)` / `N` |
| exclude_reason | 排除原因 | 条件 | `table_role=exclude` 时必填 |
| review_status | 审核状态 | 是 | `approved` / `pending` / `rejected` |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`ods_table_name`

### 3.2 `dwm_s3_subject_area`（主题域注册表）

一行一个主题域。产出格式：数据库表 / CSV。

| 字段名 | 中文说明 | 是否必填 | 取值/规则 |
|--------|----------|:--:|-----------|
| subject_area_code | 主题域编码 | 是 | 主键，2~3 大写字母 |
| subject_area_name_cn | 中文名称 | 是 | 如"交易域" |
| subject_area_name_en | 英文名称 | 是 | 如"Trade" |
| subject_area_desc | 描述 | 是 | 一句话业务范围 |
| business_scope | 业务范围 | 是 | 核心业务活动，逗号分隔 |
| owner | 负责人 | 否 | 主题域业务负责人 |
| definition_basis | 定义依据 | 是 | 自底向上聚类 + 自顶向下校验的结论 |
| updated_at | 更新时间 | 是 | 最近修改时间 |

> 主键：`subject_area_code`
>
> **命名约束**：`subject_area_code` 全局唯一，一经定义不可随意变更（下游 DWD/DWS/ADS 表名依赖此缩写）。

设计原则：
1. 主题域数量控制在 5~10 个
2. 英文缩写用于 DWD/DWS/ADS 表命名（如 `dwd_trd_order_di`）
3. 维度表按实体所属域归入，不按引用它的事实表归入

### 3.3 表关系图（可视化，非独立数据交付物）

从 `dwm_s2_field_tag WHERE core_tag='外键'` 自动生成，用于辅助人工审查。

```sql
SELECT ods_table_name AS source_table,
       col_name AS source_column,
       ref_table AS target_table,
       ref_column AS target_column,
       join_miss_rate
FROM dwm_s2_field_tag
WHERE core_tag = '外键'
  AND ref_table IS NOT NULL
  AND review_status != 'rejected';
```

### 3.4 派生查询（无需单独维护）

```sql
-- 维度候选表清单
SELECT p.ods_table_name, p.grain_statement, p.grain_keys,
       s.subject_area_code, s.subject_area_name_cn
FROM dwm_s3_table_profile p
LEFT JOIN dwm_s3_subject_area s ON p.subject_area_code = s.subject_area_code
WHERE p.table_role = 'dimension';

-- 事实候选表清单
SELECT p.ods_table_name, p.business_process, p.bp_standard_name,
       s.subject_area_code, s.subject_area_name_cn
FROM dwm_s3_table_profile p
LEFT JOIN dwm_s3_subject_area s ON p.subject_area_code = s.subject_area_code
WHERE p.table_role = 'fact';

-- 主题域下属业务过程汇总
SELECT s.subject_area_code, s.subject_area_name_cn,
       GROUP_CONCAT(p.bp_standard_name) AS business_processes
FROM dwm_s3_subject_area s
LEFT JOIN dwm_s3_table_profile p ON s.subject_area_code = p.subject_area_code AND p.table_role = 'fact'
GROUP BY s.subject_area_code, s.subject_area_name_cn;
```

---

## 4. 验收标准

### 4.1 当步必须完成（进入第四步前）

1. `dwm_s2_field_tag` 中所有 `core_tag='外键'` 且 `review_status=approved` 满足 `join_miss_rate <= 0.01`
2. `dwm_s3_table_profile` 当批次每张表有明确 `table_role`
3. 所有 `table_role=fact` 有完整的 `business_process`、`bp_standard_name`、`subject_area_code`、`grain_statement`
4. 所有 `table_role=dimension` 有 `grain_statement` 和 `grain_keys`
5. 粒度键唯一性校验通过（`grain_check_result=pass`）
6. 每个业务过程只归属一个主题域（1:1）
7. `dwm_s3_subject_area` 已定义且外键引用有效
8. 高风险歧义关系已人工确认
9. `subject_area_code` 已回填到 `dwm_s1_ods_inventory`（必填）和 `dwm_s1_source_registry`（单主题域数据源回填，跨域留空）
10. `fact_type` / `fact_type_evidence` 当步允许为空（待第四步回填）

### 4.2 第四步回写后复验

1. 所有 `table_role=fact` 的 `fact_type` 非空
2. 所有 `fact_type` 非空的记录 `fact_type_evidence` 非空

---

## 5. 与下一步衔接

- `dwm_s3_table_profile WHERE table_role='fact'` → 第四步确定事实类型与度量归属
- `dwm_s3_table_profile WHERE table_role='dimension'` → 第四步提取维度、收敛一致性维度
- `dwm_s2_field_tag WHERE core_tag='外键'` → 第四步构建矩阵的维度-事实关联线
- `dwm_s3_subject_area` → 第四步矩阵主题域列 + DWD/DWS/ADS 表命名
- `fact_candidate_final` 覆盖第二步 `fact_candidate` 初判值
- `config` 表不进入第四步维度/事实识别流程，建设阶段按需处理
