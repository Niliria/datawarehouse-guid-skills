# 字段标签标注结果 - technical_evaluation_post_delivery

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation_post_delivery |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评价-公辅设备交付后 |
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
| 11 | operational_stability_score | varchar(255) | [不可加度量] | 运行稳定性（30分） |
| 12 | operational_stability_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | equipment_stability_score | varchar(255) | [不可加度量] | 设备稳定性（30分） |
| 14 | equipment_stability_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | abnormal_issue_response_timeliness_score | varchar(255) | [不可加度量] | 异常问题响应及时性（20分） |
| 16 | abnormal_issue_response_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | missing_rectification_timeliness_score | varchar(255) | [不可加度量] | 缺陷整改及时性（10分） |
| 18 | missing_rectification_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | other_service_quality_score | varchar(255) | [不可加度量] | 其他服务质量（10分） |
| 20 | other_service_quality_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | attachment | varchar(255) | [维度属性] | 附件 |
| 22 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 23 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, operational_stability_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 技术评价表，随评价记录增长 |

**结论：** **事实表候选**（技术评价-公辅设备交付后业务过程）
