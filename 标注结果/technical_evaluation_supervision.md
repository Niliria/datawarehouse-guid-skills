# 字段标签标注结果 - technical_evaluation_supervision

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation_supervision |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评价-监理类 |
| 主题域 | 评价域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | project_to_be_evaluated | varchar(255) | [退化维度] | 待评分项目 |
| 2 | is_assessment_completed | varchar(255) | [退化维度] | 是否已完成评估 |
| 3 | contract_amount | varchar(255) | [不可加度量] | 合同金额 |
| 4 | our_company_entity | varchar(255) | [维度属性] | 我司主体 |
| 5 | supplier_name | varchar(255) | [维度属性] | 供应商名称 |
| 6 | project_type | varchar(255) | [退化维度] | 项目类型（低基数） |
| 7 | project_name | varchar(255) | [维度属性] | 项目名称 |
| 8 | project_stage | varchar(255) | [退化维度] | 项目阶段（低基数） |
| 9 | evaluator | varchar(255) | [外键] | 引用 ods_itf_po_employee_df.employeeid（评分人员） |
| 10 | business_evaluation_total_score | varchar(255) | [不可加度量] | 业务评价总分 |
| 11 | personnel_quantity_requirement_score | varchar(255) | [不可加度量] | 人员数量要求（5分） |
| 12 | personnel_quantity_requirement_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | personnel_professional_and_certificate_requirement_score | varchar(255) | [不可加度量] | 人员专业及证件要求（5分） |
| 14 | personnel_professional_and_certificate_requirement_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | project_director_score | varchar(255) | [不可加度量] | 项目总监（10分） |
| 16 | project_director_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | personnel_attendance_score | varchar(255) | [不可加度量] | 人员考勤（5分） |
| 18 | personnel_attendance_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | material_equipment_entry_score | varchar(255) | [不可加度量] | 材料设备进场（5分） |
| 20 | material_equipment_entry_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | construction_drawings_score | varchar(255) | [不可加度量] | 施工图纸（5分） |
| 22 | construction_drawings_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | construction_process_management_score | varchar(255) | [不可加度量] | 施工过程管理（10分） |
| 24 | construction_process_management_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | construction_quality_inspection_score | varchar(255) | [不可加度量] | 施工质量检查（10分） |
| 26 | construction_quality_inspection_basis | varchar(255) | [维度属性] | 评分依据 |
| 27 | on_site_monitoring_score | varchar(255) | [不可加度量] | 现场监管（10分） |
| 28 | on_site_monitoring_basis | varchar(255) | [维度属性] | 评分依据 |
| 29 | safety_supervision_plan_score | varchar(255) | [不可加度量] | 安全监理方案（10分） |
| 30 | safety_supervision_plan_basis | varchar(255) | [维度属性] | 评分依据 |
| 31 | supervision_implementation_details_score | varchar(255) | [不可加度量] | 监理实施细则（5分） |
| 32 | supervision_implementation_details_basis | varchar(255) | [维度属性] | 评分依据 |
| 33 | safety_technical_measures_and_hazard_identification_score | varchar(255) | [不可加度量] | 安全技术措施及危险源识别（10分） |
| 34 | safety_technical_measures_and_hazard_identification_basis | varchar(255) | [维度属性] | 评分依据 |
| 35 | progress_plan_formulation_score | varchar(255) | [不可加度量] | 进度计划编制（5分） |
| 36 | progress_plan_formulation_basis | varchar(255) | [维度属性] | 评分依据 |
| 37 | progress_plan_implementation_score | varchar(255) | [不可加度量] | 进度计划实施（10分） |
| 38 | progress_plan_implementation_basis | varchar(255) | [维度属性] | 评分依据 |
| 39 | progress_plan_control_score | varchar(255) | [不可加度量] | 进度计划控制（5分） |
| 40 | progress_plan_control_basis | varchar(255) | [维度属性] | 评分依据 |
| 41 | progress_remedial_measures_score | varchar(255) | [不可加度量] | 进度补救措施（10分） |
| 42 | progress_remedial_measures_basis | varchar(255) | [维度属性] | 评分依据 |
| 43 | organizational_documents_score | varchar(255) | [不可加度量] | 组织文件（10分） |
| 44 | organizational_documents_basis | varchar(255) | [维度属性] | 评分依据 |
| 45 | document_archiving_score | varchar(255) | [不可加度量] | 文档归档（10分） |
| 46 | document_archiving_basis | varchar(255) | [维度属性] | 评分依据 |
| 47 | contract_tracking_score | varchar(255) | [不可加度量] | 合同跟踪（5分） |
| 48 | contract_tracking_basis | varchar(255) | [维度属性] | 评分依据 |
| 49 | claims_and_disputes_score | varchar(255) | [不可加度量] | 索赔及纠纷（10分） |
| 50 | claims_and_disputes_basis | varchar(255) | [维度属性] | 评分依据 |
| 51 | hazard_inspection_and_monitoring_score | varchar(255) | [不可加度量] | 危险检查及监督（10分） |
| 52 | hazard_inspection_and_monitoring_basis | varchar(255) | [维度属性] | 评分依据 |
| 53 | special_situation_coordination_score | varchar(255) | [不可加度量] | 特殊情况协调（5分） |
| 54 | special_situation_coordination_basis | varchar(255) | [维度属性] | 评分依据 |
| 55 | technical_problem_review_and_tracking_score | varchar(255) | [不可加度量] | 技术问题评审与跟踪（10分） |
| 56 | technical_problem_review_and_tracking_basis | varchar(255) | [维度属性] | 评分依据 |
| 57 | cross_operations_score | varchar(255) | [不可加度量] | 交叉作业（10分） |
| 58 | cross_operations_basis | varchar(255) | [维度属性] | 评分依据 |
| 59 | integrity_situation_score | varchar(255) | [不可加度量] | 廉洁情况（10分） |
| 60 | integrity_situation_basis | varchar(255) | [维度属性] | 评分依据 |
| 61 | attachment | varchar(255) | [维度属性] | 附件 |
| 62 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 63 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

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

**结论：** **事实表候选**（技术评价-监理类业务过程）
