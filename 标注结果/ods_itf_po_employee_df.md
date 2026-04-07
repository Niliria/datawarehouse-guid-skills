# 字段标签标注结果 - ods_itf_po_employee_df

## 一、表基本信息

| 项目 | 内容 |
|------|------|
| 表名 | ods_itf_po_employee_df |
| 库名 | yummy |
| 行数 | 0（空表） |
| 表注释 | 接口-PO-人员数据同步 |
| 主题域 | 组织域/员工域 |

## 二、字段标注结果

| 序号 | 字段名 | 数据类型 | 标签 | 关联实体/说明 |
|------|--------|---------|------|---------------|
| 1 | perioddate | varchar(255) | [业务时间] | 周期日期（分区字段） |
| 2 | employeeid | varchar(255) | [业务键] | 员工ID，唯一标识员工 |
| 3 | employeename | varchar(255) | [维度属性] | 员工名称 |
| 4 | managerid | varchar(255) | [外键] | 引用 ods_itf_po_employee_df.employeeid（上级经理） |
| 5 | departl1 | varchar(255) | [维度属性] | 部门L1 |
| 6 | departl1name | varchar(255) | [维度属性] | 部门L1名称 |
| 7 | departl2 | varchar(255) | [维度属性] | 部门L2 |
| 8 | departl2name | varchar(255) | [维度属性] | 部门L2名称 |
| 9 | departl3 | varchar(255) | [维度属性] | 部门L3 |
| 10 | departl3name | varchar(255) | [维度属性] | 部门L3名称 |
| 11 | departl4 | varchar(255) | [维度属性] | 部门L4 |
| 12 | departl4name | varchar(255) | [维度属性] | 部门L4名称 |
| 13 | departl5 | varchar(255) | [维度属性] | 部门L5 |
| 14 | departl5name | varchar(255) | [维度属性] | 部门L5名称 |
| 15 | hiredate | varchar(255) | [业务时间] | 入职日期 |
| 16 | termdate | varchar(255) | [业务时间] | 离职日期 |
| 17 | jobstatus | varchar(255) | [退化维度] | 工作状态（低基数） |
| 18 | birthday | varchar(255) | [业务时间] | 生日 |
| 19 | updatedtime | varchar(255) | [技术时间] | 更新时间 |
| 20 | companyclassification | varchar(255) | [退化维度] | 公司分类 |
| 21 | officelocation | varchar(255) | [维度属性] | 办公地点 |
| 22 | departcode | varchar(255) | [维度属性] | 部门代码 |
| 23 | parentdepartcode | varchar(255) | [维度属性] | 父部门代码 |
| 24 | companyname | varchar(255) | [维度属性] | 公司名称 |
| 25 | jobname | varchar(255) | [维度属性] | 职位名称 |
| 26 | telephonenumber | varchar(255) | [维度属性] | 电话号码 |
| 27 | dingtalkid | varchar(255) | [维度属性] | 钉钉ID |

## 三、标注验证

- [x] 所有字段都有标签
- [x] 主键已标注：employeeid [业务键]
- [x] 外键已标注：managerid [外键] → ods_itf_po_employee_df.employeeid
- [x] 度量：无度量字段
- [x] 时间已区分：perioddate, hiredate, termdate, birthday [业务时间]，updatedtime [技术时间]
- [x] 退化维度已识别：jobstatus, companyclassification
- [x] 技术字段已标注：updatedtime [技术时间]
- [x] 无矛盾标签

## 四、扩展标签补充

### [层级属性]
- departl1, departl2, departl3, departl4, departl5 [层级属性][L1-L5]
- 父子层级关系：departl1 → departl2 → departl3 → departl4 → departl5

### [SCD 属性]
- jobstatus [SCD 属性]（员工状态会变化）
- employeename [SCD 属性]（可能改名）
- jobname [SCD 属性]（职位会变化）
- officelocation [SCD 属性]（办公地点会变化）

## 五、表类型判断

| 判断项 | 结果 | 说明 |
|--------|------|------|
| 有 [业务键]？ | ✓ | employeeid |
| 有 [外键]？ | ✓ | managerid（自引用） |
| 有 [度量]？ | ✗ | 无度量 |
| 有 [业务时间]？ | ✓ | hiredate, termdate, birthday |
| 持续增长？ | ✗ | 员工维表，基本稳定 |

**结论：** **维度表**（员工维度表）

## 六、待确认事项

| 序号 | 问题 | 建议 | 状态 |
|------|------|------|------|
| 1 | employeeid 是否真正唯一？ | 需采样验证唯一性 | 待确认 |
| 2 | perioddate 是否为日期分区字段？ | 建议验证数据内容 | 待确认 |

## 七、下一步

标注结果汇总到：
1. **业务键清单**：employeeid
2. **外键关系清单**：managerid → ods_itf_po_employee_df.employeeid
3. **维度属性清单**：employeename, departl1, departl2 等
4. **业务时间清单**：perioddate, hiredate, termdate, birthday
