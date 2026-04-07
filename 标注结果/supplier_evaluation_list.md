# 字段标签标注结果 - supplier_evaluation_list

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | supplier_evaluation_list |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 供应商参评名单 |
| 主题域 | 供应商域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | index_column | varchar(255) | [业务键] | 索引列，唯一标识供应商参评记录 |
| 2 | supplier_name | varchar(255) | [维度属性] | 供应商名称 |
| 3 | evaluation_cycle | varchar(255) | [维度属性] | 考核周期 |
| 4 | supplier_notification_email | varchar(255) | [维度属性] | 供应商通知邮箱 |
| 5 | project_type | varchar(255) | [退化维度] | 项目类型（低基数） |
| 6 | department | varchar(255) | [维度属性] | 部门 |
| 7 | project_name | varchar(255) | [维度属性] | 项目名称 |
| 8 | project_contract_amount | varchar(255) | [不可加度量] | 项目/合同金额（万元） |
| 9 | engineering_name_with_supplementary_agreement | varchar(255) | [维度属性] | 工程名称（含补充协议） |
| 10 | our_company_entity | varchar(255) | [维度属性] | 我司主体 |
| 11 | project_stage | varchar(255) | [退化维度] | 项目阶段（低基数） |
| 12 | technical_responsible_person | varchar(255) | [维度属性] | 技术负责人 |
| 13 | technical_responsible_person_score_confirmation | varchar(255) | [退化维度] | 技术负责人评分确认 |
| 14 | notify_technical_responsible_person | varchar(255) | [退化维度] | 通知技术负责人 |
| 15 | procurement_manager_score_confirmation | varchar(255) | [退化维度] | 采购经理评分确认 |
| 16 | project_manager | varchar(255) | [维度属性] | 项目经理 |
| 17 | project_manager_score_confirmation | varchar(255) | [退化维度] | 项目经理评分确认 |
| 18 | notify_project_manager | varchar(255) | [退化维度] | 通知项目经理 |
| 19 | technical_evaluator | varchar(255) | [维度属性] | 技术评分人 |
| 20 | commercial_evaluator | varchar(255) | [维度属性] | 商务评分人 |
| 21 | commercial_responsible_person_contact_email | varchar(255) | [维度属性] | 商务负责人.联系邮箱 |
| 22 | remarks | varchar(255) | [维度属性] | 备注 |
| 23 | business_evaluation_form | varchar(255) | [维度属性] | 业务评分表 |
| 24 | procurement_evaluation_form | varchar(255) | [维度属性] | 采购评分表 |
| 25 | technical_score | varchar(255) | [不可加度量] | 技术评分 |
| 26 | technical_comprehensive_score | varchar(255) | [不可加度量] | 技术综合评分 |
| 27 | technical_score_assistance | varchar(255) | [维度属性] | 技术评分辅助 |
| 28 | commercial_score | varchar(255) | [不可加度量] | 商务评分 |
| 29 | commercial_comprehensive_score | varchar(255) | [不可加度量] | 商务综合评分 |
| 30 | contract_performance_evaluation_comprehensive_score | varchar(255) | [不可加度量] | 履约评价综合得分 |
| 31 | supplier_rating | varchar(255) | [退化维度] | 供应商评级（低基数） |
| 32 | notify_technical_evaluator | varchar(255) | [退化维度] | 通知技术评分人 |
| 33 | urge_technical_score | varchar(255) | [退化维度] | 催促技术评分 |
| 34 | urge_procurement_score | varchar(255) | [退化维度] | 催促采购评分 |
| 35 | notify_commercial_evaluator | varchar(255) | [退化维度] | 通知商务评分人 |
| 36 | score_attachment | varchar(255) | [维度属性] | 评分附件 |
| 37 | generate_score_attachment | varchar(255) | [维度属性] | 生成评分附件 |
| 38 | commercial_responsible_person_contact_email_copy | varchar(255) | [维度属性] | 商务负责人.联系邮箱 副本 |
| 39 | notify_commercial_responsible_person | varchar(255) | [退化维度] | 通知商务负责人 |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 主键已标注：index_column [业务键]
- [x] 外键：无外键字段
- [x] 度量已标注：technical_score, technical_comprehensive_score, commercial_score, commercial_comprehensive_score, contract_performance_evaluation_comprehensive_score [不可加度量]
- [x] 时间：无时间字段
- [x] 退化维度已识别：project_type, project_stage, supplier_rating 等
- [x] 技术字段：无技术字段
- [x] 无矛盾标签

## 四、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✓ | index_column |
| 有 [外键]？ | ✗ | 无外键 |
| 有 [度量]？ | ✓ | technical_score, commercial_score 等 [不可加度量] |
| 有 [业务时间]？ | ✗ | 无时间字段 |
| 持续增长？ | 待验证 | 需采样验证数据增长趋势 |

**结论：** 可能是**维度表候选**（供应商参评名单维度）

## 五、待确认事项

| 序号 | 问题 | 建议 | 状态 |
|------|------|------|------|
| 1 | index_column 是否真正唯一？ | 需采样验证唯一性 | 待确认 |
| 2 | project_contract_amount 应该是数值型？ | 字段类型为 varchar，建议验证数据内容 | 待确认 |

## 六、下一步

标注结果汇总到：
1. **业务键清单**：index_column
2. **度量清单**：technical_score, technical_comprehensive_score, commercial_score, commercial_comprehensive_score, contract_performance_evaluation_comprehensive_score [不可加度量]
3. **维度属性清单**：supplier_name, department, project_name 等
4. **退化维度清单**：project_type, project_stage, supplier_rating 等
