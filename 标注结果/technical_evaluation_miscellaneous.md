# 字段标签标注结果 - technical_evaluation_miscellaneous

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation_miscellaneous |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评价-零星工程、机电、其他施工 |
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
| 11 | personnel_quantity_requirement_score | varchar(255) | [不可加度量] | 人员数量要求（5分） |
| 12 | personnel_quantity_requirement_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | personnel_professional_qualification_score | varchar(255) | [不可加度量] | 人员专业资质（5分） |
| 14 | personnel_professional_qualification_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | project_manager_score | varchar(255) | [不可加度量] | 项目经理（10分） |
| 16 | project_manager_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | personnel_attendance_score | varchar(255) | [不可加度量] | 人员考勤（5分） |
| 18 | personnel_attendance_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | organizational_tool_score | varchar(255) | [不可加度量] | 组织工具（10分） |
| 20 | organizational_tool_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | construction_deployment_plan_score | varchar(255) | [不可加度量] | 施工部署方案（10分） |
| 22 | construction_deployment_plan_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | construction_personnel_quality_control_score | varchar(255) | [不可加度量] | 施工人员质量控制（10分） |
| 24 | construction_personnel_quality_control_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | construction_machinery_quality_control_score | varchar(255) | [不可加度量] | 施工机械质量控制（10分） |
| 26 | construction_machinery_quality_control_basis | varchar(255) | [维度属性] | 评分依据 |
| 27 | material_quality_control_score | varchar(255) | [不可加度量] | 材料质量控制（10分） |
| 28 | material_quality_control_basis | varchar(255) | [维度属性] | 评分依据 |
| 29 | process_technology_quality_control_score | varchar(255) | [不可加度量] | 工序工艺质量控制（10分） |
| 30 | process_technology_quality_control_basis | varchar(255) | [维度属性] | 评分依据 |
| 31 | system_debugging_score | varchar(255) | [不可加度量] | 系统调试（10分） |
| 32 | system_debugging_basis | varchar(255) | [维度属性] | 评分依据 |
| 33 | construction_drawing_review_technical_briefing_score | varchar(255) | [不可加度量] | 施工图审查技术交底（5分） |
| 34 | construction_drawing_review_technical_briefing_basis | varchar(255) | [维度属性] | 评分依据 |
| 35 | major_quality_defects_score | varchar(255) | [不可加度量] | 重大质量缺陷（10分） |
| 36 | major_quality_defects_basis | varchar(255) | [维度属性] | 评分依据 |
| 37 | quality_defect_rectification_score | varchar(255) | [不可加度量] | 质量缺陷整改（5分） |
| 38 | quality_defect_rectification_basis | varchar(255) | [维度属性] | 评分依据 |
| 39 | safety_system_score | varchar(255) | [不可加度量] | 安全体系（10分） |
| 40 | safety_system_basis | varchar(255) | [维度属性] | 评分依据 |
| 41 | civilized_construction_measures_score | varchar(255) | [不可加度量] | 文明施工措施（10分） |
| 42 | civilized_construction_measures_basis | varchar(255) | [维度属性] | 评分依据 |
| 43 | safety_qualification_score | varchar(255) | [不可加度量] | 安全资质（5分） |
| 44 | safety_qualification_basis | varchar(255) | [维度属性] | 评分依据 |
| 45 | personnel_safety_score | varchar(255) | [不可加度量] | 人员安全（10分） |
| 46 | personnel_safety_basis | varchar(255) | [维度属性] | 评分依据 |
| 47 | special_operations_score | varchar(255) | [不可加度量] | 特种作业（5分） |
| 48 | special_operations_basis | varchar(255) | [维度属性] | 评分依据 |
| 49 | material_equipment_safety_score | varchar(255) | [不可加度量] | 材料设备安全（5分） |
| 50 | material_equipment_safety_basis | varchar(255) | [维度属性] | 评分依据 |
| 51 | hazard_and_risk_handling_score | varchar(255) | [不可加度量] | 危险源及风险处理（10分） |
| 52 | hazard_and_risk_handling_basis | varchar(255) | [维度属性] | 评分依据 |
| 53 | safety_protection_measures_score | varchar(255) | [不可加度量] | 安全防护措施（10分） |
| 54 | safety_protection_measures_basis | varchar(255) | [维度属性] | 评分依据 |
| 55 | schedule_plan_score | varchar(255) | [不可加度量] | 进度计划（10分） |
| 56 | schedule_plan_basis | varchar(255) | [维度属性] | 评分依据 |
| 57 | schedule_progress_score | varchar(255) | [不可加度量] | 进度推进（10分） |
| 58 | schedule_progress_basis | varchar(255) | [维度属性] | 评分依据 |
| 59 | human_material_machine_impact_score | varchar(255) | [不可加度量] | 人材机影响（10分） |
| 60 | human_material_machine_impact_basis | varchar(255) | [维度属性] | 评分依据 |
| 61 | cross_operation_score | varchar(255) | [不可加度量] | 交叉作业（5分） |
| 62 | cross_operation_basis | varchar(255) | [维度属性] | 评分依据 |
| 63 | coordination_meeting_organization_score | varchar(255) | [不可加度量] | 协调会组织（5分） |
| 64 | coordination_meeting_organization_basis | varchar(255) | [维度属性] | 评分依据 |
| 65 | meeting_attendance_score | varchar(255) | [不可加度量] | 会议出席（5分） |
| 66 | meeting_attendance_basis | varchar(255) | [维度属性] | 评分依据 |
| 67 | response_speed_score | varchar(255) | [不可加度量] | 响应速度（10分） |
| 68 | response_speed_basis | varchar(255) | [维度属性] | 评分依据 |
| 69 | attachment | varchar(255) | [维度属性] | 附件 |
| 70 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 71 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, personnel_quantity_requirement_score 等 [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | business_evaluation_total_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 技术评价表，随评价记录增长 |

**结论：** **事实表候选**（技术评价-零星工程、机电、其他施工业务过程）
