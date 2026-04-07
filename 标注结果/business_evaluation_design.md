# 字段标签标注结果 - business_evaluation_design

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | business_evaluation_design |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 商务评分【设计类】 |
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
| 11 | contract_performance_score | varchar(255) | [不可加度量] | 合同履约（10分） |
| 12 | contract_performance_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | quotation_visa_score | varchar(255) | [不可加度量] | 报价、签证（10分） |
| 14 | quotation_visa_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | payment_terms_score | varchar(255) | [不可加度量] | 付款条件（10分） |
| 16 | payment_terms_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | payment_request_score | varchar(255) | [不可加度量] | 请款（10分） |
| 18 | payment_request_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | business_contract_dispute_score | varchar(255) | [不可加度量] | 商务合同纠纷（10分） |
| 20 | business_contract_dispute_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | design_change_cost_score | varchar(255) | [不可加度量] | 设计变更费用（30分） |
| 22 | design_change_cost_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | project_budget_score | varchar(255) | [不可加度量] | 工程概算（20分） |
| 24 | project_budget_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | attachment | varchar(255) | [维度属性] | 附件 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, contract_performance_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 商务评分表，随评分记录增长 |

**结论：** **事实表候选**（商务评价-设计类业务过程）
