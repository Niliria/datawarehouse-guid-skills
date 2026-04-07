# 字段标签标注结果 - technical_evaluation

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | technical_evaluation |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 技术评分【公辅设备-交付前】——规划部 |
| 主题域 | 评价域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | project_to_be_evaluated | varchar(255) | [退化维度] | 待评分项目 |
| 2 | is_assessment_completed | varchar(255) | [退化维度] | 是否已完成评估 |
| 3 | evaluator | varchar(255) | [外键] | 引用 ods_itf_po_employee_df.employeeid（评分人） |
| 4 | business_evaluation_total_score | varchar(255) | [不可加度量] | 业务评价总分 |
| 5 | contract_amount | varchar(255) | [不可加度量] | 合同金额 |
| 6 | our_company_entity | varchar(255) | [维度属性] | 我司主体 |
| 7 | supplier_name | varchar(255) | [维度属性] | 供应商名称 |
| 8 | project_type | varchar(255) | [退化维度] | 项目类型（低基数） |
| 9 | project_name | varchar(255) | [维度属性] | 项目名称 |
| 10 | project_stage | varchar(255) | [退化维度] | 项目阶段（低基数） |
| 11 | equipment_technical_parameter_match_score | varchar(255) | [不可加度量] | 设备核心部分技术参数与部件的匹配度（20分） |
| 12 | equipment_technical_parameter_match_basis | varchar(255) | [维度属性] | 评分依据 |
| 13 | auxiliary_equipment_completeness_score | varchar(255) | [不可加度量] | 公辅设备方案的完整性（20分） |
| 14 | auxiliary_equipment_completeness_basis | varchar(255) | [维度属性] | 评分依据 |
| 15 | auxiliary_equipment_risk_identification_score | varchar(255) | [不可加度量] | 公辅设备方案风险识别与处理（20分） |
| 16 | auxiliary_equipment_risk_identification_basis | varchar(255) | [维度属性] | 评分依据 |
| 17 | supplier_on_site_technical_capability_score | varchar(255) | [不可加度量] | 供应商设备现场技术处理能力（10分） |
| 18 | supplier_on_site_technical_capability_basis | varchar(255) | [维度属性] | 评分依据 |
| 19 | supplier_change_professionalism_score | varchar(255) | [不可加度量] | 供应商对需求变更的专业度(10分) |
| 20 | supplier_change_professionalism_basis | varchar(255) | [维度属性] | 评分依据 |
| 21 | supplier_change_cooperation_score | varchar(255) | [不可加度量] | 供应商对需求变更配合度(10分) |
| 22 | supplier_change_cooperation_basis | varchar(255) | [维度属性] | 评分依据 |
| 23 | auxiliary_equipment_inspection_timeliness_score | varchar(255) | [不可加度量] | 公辅设备特检报验的及时性(10分) |
| 24 | auxiliary_equipment_inspection_timeliness_basis | varchar(255) | [维度属性] | 评分依据 |
| 25 | attachment | varchar(255) | [维度属性] | 附件 |
| 26 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 27 | department | varchar(255) | [维度属性] | 部门 |
| 28 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 主键：无明显主键字段（所有字段都为 nullable）
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：business_evaluation_total_score, contract_amount, equipment_technical_parameter_match_score 等 [不可加度量]
- [x] 时间：无时间字段
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage
- [x] 技术字段：无技术字段
- [x] 无矛盾标签

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator（引用员工表） |
| 有 [度量]？ | ✓ | business_evaluation_total_score, contract_amount 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 技术评分表，随评分记录增长 |

**结论：** **事实表候选**（技术评价业务过程）

## 五、待确认事项

| 序号 | 问题 | 建议 | 状态 |
|------|------|------|------|
| 1 | 缺少主键字段？ | 建议检查表结构，确认是否有隐藏主键 | 待确认 |
| 2 | 缺少业务时间字段？ | 建议增加 evaluation_date（评价日期） | 待确认 |
| 3 | 所有度量字段都是 varchar？ | 建议验证数据内容，应为数值型 | 待确认 |

## 六、下一步

标注结果汇总到：
1. **外键关系清单**：evaluator → ods_itf_po_employee_df.employeeid
2. **度量清单**：business_evaluation_total_score, contract_amount, equipment_technical_parameter_match_score 等 [不可加度量]
3. **退化维度清单**：project_to_be_evaluated, is_assessment_completed, project_type, project_stage
4. **维度属性清单**：our_company_entity, supplier_name, project_name 等
