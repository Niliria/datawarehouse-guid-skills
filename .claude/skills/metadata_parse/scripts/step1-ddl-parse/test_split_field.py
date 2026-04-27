#!/usr/bin/env python3
"""测试字段名拆解功能"""

from export_all_tables_to_single_sheet import split_field_name

# 测试用例
test_cases = [
    'updatedtime',
    'createddate',
    'deletedstatus',
    'termdate',
    'jobstatus',
    'term_date',
    'job_status',
    'user_id',
    'UserName',
    'createTime',
    'job123status',
    'simple',
    'ID',
    'update',
    'id',
    'departl1',
    'companyclassification',
    'officelocation',
    'parentdepart',
    'telephonenumber'
]

print("测试字段名拆解功能：")
print("-" * 50)

for test_case in test_cases:
    result = split_field_name(test_case)
    print(f"输入: {test_case}")
    print(f"输出: {result}")
    print()

print("-" * 50)
print("测试完成！")
