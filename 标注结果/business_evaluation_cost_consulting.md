# 字段标签标注结果 - business_evaluation_cost_consulting

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | business_evaluation_cost_consulting |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 商务评分【造价咨询类】 |
| 主题域 | 评价域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | project_to_be_evaluated | varchar(255) | [退化维度] | 待评分项目 |
| 2 | is_assessment_completed | varchar(255) | [退化维度] | 是否已完成评估 |
| 3 | evaluator | varchar(255) | [外键] | 引用 ods_itf_po_employee_df.employeeid（评分人员） |
| 4 | business_evaluation_total_score | varchar(255) | [不可加度量] | 业务评价总分 |
| 5 | contract_amount | varchar(255) | [不可加度量] | 合同金额 |
| 6 | our_company_entity | varchar(255) | [维度属性] | 我司主体 |
| 7 | supplier_name | varchar(255) | [维度属性] | 供应商名称 |
| 8 | project_type | varchar(255) | [退化维度] | 项目类型（低基数） |
| 9 | project_name | varchar(255) | [维度属性] | 项目名称 |
| 10 | project_stage | varchar(255) | [退化维度] | 项目阶段（低基数） |
| 11 | bidding_contract_score | varchar(255) | [不可加度量] | 招标合同（15分） |
| 12 | bidding_contract_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | quotation_visa_score | varchar(255) | [不可加度量] | 报价、签证（20分） |
| 14 | quotation_visa_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | payment_terms_score | varchar(255) | [不可加度量] | 付款条件（15分） |
| 16 | payment_terms_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | performance_score | varchar(255) | [不可加度量] | 履约情况（30分） |
| 18 | performance_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | payment_review_timeliness_and_accuracy_score | varchar(255) | [不可加度量] | 付款审核及时性及准确性（20分） |
| 20 | payment_review_timeliness_and_accuracy_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | rationalization_suggestions_bonus_score | varchar(255) | [不可加度量] | 合理化建议情况加分项 |
| 22 | rationalization_suggestions_bonus_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | attachment | varchar(255) | [维度属性] | 附件 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, bidding_contract_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage
- [x] 无时间字段
- [x] 无技术字段

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 商务评分表，随评分记录增长 |

**结论：** **事实表候选**（商务评价-造价咨询类业务过程）

## 五、待确认事项

| 序号 | 问题 | 建议 | 状态 |
|------|------|------|------|
| 1 | 缺少主键字段？ | 建议检查表结构 | 待确认 |
| 2 | 缺少业务时间字段？ | 建议增加 evaluation_date | 待确认 |

## 六、下一步

标注结果汇总到：
1. **外键关系清单**：evaluator → ods_itf_po_employee_df.employeeid
2. **度量清单**：business_evaluation_total_score, contract_amount, bidding_contract_score 等 [不可加度量]
3. **退化维度清单**：project_to_be_evaluated, is_assessment_completed, project_type, project_stage
