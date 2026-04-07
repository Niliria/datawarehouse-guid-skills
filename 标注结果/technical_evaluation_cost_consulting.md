# 字段标签标注结果 - technical_evaluation_cost_consulting

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation_cost_consulting |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评价-造价咨询类 |
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
| 11 | consulting_unit_cooperation_score | varchar(255) | [不可加度量] | 咨询单位配合度（10分） |
| 12 | consulting_unit_cooperation_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | project_plan_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 项目策划准确性与时效性（15分） |
| 14 | project_plan_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | bidding_budget_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 招标预算准确性与时效性（15分） |
| 16 | bidding_budget_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | budget_conversion_review_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 预算转审核准确性与时效性（10分） |
| 18 | budget_conversion_review_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | site_visa_change_review_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 现场签证变更审核准确性与时效性（10分） |
| 20 | site_visa_change_review_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | settlement_review_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 结算审核准确性与时效性（10分） |
| 22 | settlement_review_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | progress_payment_review_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 进度款审核准确性与时效性（10分） |
| 24 | progress_payment_review_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | material_inquiry_accuracy_and_timeliness_score | varchar(255) | [不可加度量] | 甲定乙供材料询价准确性与时效性（10分） |
| 26 | material_inquiry_accuracy_and_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 27 | document_management_score | varchar(255) | [不可加度量] | 资料管理（10分） |
| 28 | document_management_basis | varchar(255) | [维度属性] | 评分依据 |
| 29 | additional_contribution_bonus_score | varchar(255) | [不可加度量] | 额外贡献加分（10分） |
| 30 | additional_contribution_bonus_basis | varchar(255) | [维度属性] | 评分依据 |
| 31 | attachment | varchar(255) | [维度属性] | 附件 |
| 32 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 33 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, consulting_unit_cooperation_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 技术评价表，随评价记录增长 |

**结论：** **事实表候选**（技术评价-造价咨询类业务过程）
