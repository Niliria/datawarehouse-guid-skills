# 字段标签标注结果（示例：technical_evaluation 表）

> 本文档记录 `technical_evaluation` 表的字段标注结果，作为标注模板和示例。

---

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation |
| 库名 | yummy |
| 行数 | 待统计 |
| 表注释 | 技术评价主表 |
| 主题域 | 评价域（待确认） |

---

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | id | int | [代理键] | 自增主键，系统生成 |
| 2 | evaluation_id | varchar(64) | [业务键] | 评价主键，业务系统生成 |
| 3 | supplier_id | varchar(64) | [外键] | 引用 supplier_evaluation_list.supplier_id |
| 4 | project_id | varchar(64) | [外键] | 引用项目表（需确认具体表名） |
| 5 | evaluator_id | varchar(64) | [外键] | 引用 ods_itf_po_employee_df.employee_id |
| 6 | score | decimal(5,2) | [不可加度量] | 评分（0-100），不可直接加总 |
| 7 | evaluation_type | varchar(20) | [退化维度] | 评价类型（低基数枚举） |
| 8 | evaluation_date | datetime | [业务时间] | 评价动作发生时间 |
| 9 | create_time | datetime | [业务时间] | 记录创建时间 |
| 10 | update_time | datetime | [技术时间] | 系统更新时间 |
| 11 | is_deleted | tinyint(1) | [技术字段] | 逻辑删除标记 |

---

## 三、标注验证

### 3.1 检查清单

- [x] 所有字段都有标签
- [x] 主键已标注：id [代理键], evaluation_id [业务键]
- [x] 外键已标注：supplier_id, project_id, evaluator_id
- [x] 度量已标注：score [不可加度量]
- [x] 时间已区分：evaluation_date/create_time [业务时间]，update_time [技术时间]
- [x] 退化维度已识别：evaluation_type
- [x] 技术字段已排除：is_deleted
- [x] 无矛盾标签

---

### 3.2 采样验证

#### 3.2.1 验证主键唯一性

```sql
SELECT COUNT(*) AS total, COUNT(DISTINCT evaluation_id) AS distinct_count
FROM technical_evaluation;
-- 结果：total = distinct_count → 唯一
```

#### 3.2.2 验证外键关系

```sql
-- 验证 supplier_id
SELECT COUNT(*) AS not_found
FROM technical_evaluation a
LEFT JOIN supplier_evaluation_list b ON a.supplier_id = b.supplier_id
WHERE b.supplier_id IS NULL;
-- 结果：0 → 外键关系成立

-- 验证 evaluator_id
SELECT COUNT(*) AS not_found
FROM technical_evaluation a
LEFT JOIN ods_itf_po_employee_df b ON a.evaluator_id = b.employee_id
WHERE b.employee_id IS NULL;
-- 结果：0 → 外键关系成立
```

#### 3.2.3 验证低基数（退化维度）

```sql
SELECT COUNT(DISTINCT evaluation_type) AS unique_count
FROM technical_evaluation;
-- 结果：< 10 → 低基数，确认为退化维度
```

#### 3.2.4 验证度量范围

```sql
SELECT MIN(score), MAX(score), AVG(score)
FROM technical_evaluation;
-- 结果：0-100 → 评分，不可加总
```

---

## 四、表类型判断（用于第三步）

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✓ | evaluation_id |
| 有 [外键]？ | ✓ | supplier_id, project_id, evaluator_id |
| 有 [度量]？ | ✓ | score |
| 有 [业务时间]？ | ✓ | evaluation_date, create_time |
| 持续增长？ | 待验证 | 需采样验证数据增长趋势 |

**初步结论：** 可能是**事实表候选**（技术评价业务过程）

---

## 五、待确认事项

| 序号 | 字段名 | 问题 | 建议 | 状态 |
|------|--------|------|------|------|
| 1 | project_id | 引用表不明确 | 需查询所有含 project_id 的表 | 待确认 |
| 2 | — | 表是否持续增长 | 采样验证最近 7 天的数据量变化 | 待验证 |

---

## 六、下一步

标注完成后，将本表的标注结果汇总到：

1. **业务键清单**：evaluation_id
2. **外键关系清单**：supplier_id → supplier_evaluation_list, evaluator_id → ods_itf_po_employee_df
3. **度量清单**：score [不可加度量]
4. **业务时间清单**：evaluation_date, create_time

然后进入**第三步：通过 [ID] 字段画表关系图**。
