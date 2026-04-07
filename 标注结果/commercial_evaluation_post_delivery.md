# 字段标签标注结果 - commercial_evaluation_post_delivery

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | commercial_evaluation_post_delivery |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 商务评分【公辅设备-交付后】 |
| 主题域 | 评价域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | project_to_be_evaluated | varchar(255) | [退化维度] | 待评分项目 |
| 2 | is_assessment_completed | varchar(255) | [退化维度] | 是否已完成评估 |
| 3 | evaluator | varchar(255) | [外键] | 引用 ods_itf_po_employee_df.employeeid（评分人员） |
| 4 | complaint_safety_penalty_cooperation_deduction_score | varchar(255) | [不可加度量] | 投诉&安全处罚&配合度(15分)（扣分项） |
| 5 | contract_amount | varchar(255) | [不可加度量] | 合同金额 |
| 6 | our_company_entity | varchar(255) | [维度属性] | 我司主体 |
| 7 | supplier_name | varchar(255) | [维度属性] | 供应商名称 |
| 8 | project_type | varchar(255) | [退化维度] | 项目类型（低基数） |
| 9 | project_name | varchar(255) | [维度属性] | 项目名称 |
| 10 | project_stage | varchar(255) | [退化维度] | 项目阶段（低基数） |
| 11 | complaint_safety_penalty_cooperation_deduction_basis | varchar(255) | [维度属性] | 评分依据 |
| 12 | attachment | varchar(255) | [维度属性] | 附件 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 外键已标注：evaluator [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量已标注：complaint_safety_penalty_cooperation_deduction_score, contract_amount [不可加度量]
- [x] 退化维度已识别：project_to_be_evaluated, is_assessment_completed, project_type, project_stage

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✗ | 无明确业务键 |
| 有 [外键]？ | ✓ | evaluator |
| 有 [度量]？ | ✓ | complaint_safety_penalty_cooperation_deduction_score, contract_amount [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | ✓ | 商业评分表，随评分记录增长 |

**结论：** **事实表候选**（商业评价-公辅设备交付后业务过程）
