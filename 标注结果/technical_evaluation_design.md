# 字段标签标注结果 - technical_evaluation_design

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation_design |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评价-设计类 |
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
| 11 | chief_designer_requirement_score | varchar(255) | [不可加度量] | 总设计师要求（10分） |
| 12 | chief_designer_requirement_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | designer_count_score | varchar(255) | [不可加度量] | 设计人员数量（10分） |
| 14 | designer_count_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | design_file_submission_timeliness_score | varchar(255) | [不可加度量] | 设计文件提交及时性（10分） |
| 16 | design_file_submission_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | design_change_feedback_timeliness_score | varchar(255) | [不可加度量] | 设计变更反馈及时性（10分） |
| 18 | design_change_feedback_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | first_version_design_defects_score | varchar(255) | [不可加度量] | 首版设计缺陷（10分） |
| 20 | first_version_design_defects_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | final_version_design_defects_score | varchar(255) | [不可加度量] | 最终版设计缺陷（10分） |
| 22 | final_version_design_defects_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | construction_drawings_delivery_score | varchar(255) | [不可加度量] | 施工图交付（10分） |
| 24 | construction_drawings_delivery_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | assistance_service_score | varchar(255) | [不可加度量] | 配合服务（10分） |
| 26 | assistance_service_basis | varchar(255) | [维度属性] | 评分依据 |
| 27 | response_speed_and_cooperation_score | varchar(255) | [不可加度量] | 响应速度及配合度（10分） |
| 28 | response_speed_and_cooperation_basis | varchar(255) | [维度属性] | 评分依据 |
| 29 | review_opinion_communication_score | varchar(255) | [不可加度量] | 审图意见交流（10分） |
| 30 | review_opinion_communication_basis | varchar(255) | [维度属性] | 评分依据 |
| 31 | innovation_and_cost_reduction_bonus_score | varchar(255) | [不可加度量] | 创新及降本加分（10分） |
| 32 | innovation_and_cost_reduction_bonus_basis | varchar(255) | [维度属性] | 评分依据 |
| 33 | attachment | varchar(255) | [维度属性] | 附件 |
| 34 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 35 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, chief_designer_requirement_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 技术评价表，随评价记录增长 |

**结论：** **事实表候选**（技术评价-设计类业务过程）
