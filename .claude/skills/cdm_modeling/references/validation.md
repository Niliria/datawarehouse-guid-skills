# 产物生成与校验门禁

将 DIM/DWD 设计字典渲染为 SQL 和结构化清单，并对输入、模型结构、引用关系和模板输出执行门禁。

## 输出目录

```text
output/cdm-modeling/
├── ddl/
│   ├── dim/
│   └── dwd/
├── etl/
│   ├── dim/
│   └── dwd/
└── docs/
    ├── dim_list.csv
    ├── dwd_list.csv
    ├── field_mapping.csv
    ├── dependency.csv
    ├── model_design.md
    └── validation_report.md
```

## 生成规则

1. 让模板只消费设计字典，不在模板中推断业务语义。
2. 让源表和源字段全部来自上游文档或解析后的设计字典。
3. 使用 DIM spec 的业务键类型，不统一强制转成 STRING。
4. 在 DWD DDL/ETL 中保留粒度键、代理键、明细描述字段和度量。
5. 在 `field_mapping.csv` 中覆盖业务键、粒度键、维度属性、维度代理键、明细字段和度量。
6. 在 `dependency.csv` 中只记录事实实际引用的 DIM，不依赖所有维度。
7. 覆盖同次执行的旧产物，并在生成后自动执行校验。

## 文档产物

| 文件 | 内容 |
|---|---|
| `dim_list.csv` | DIM 表、业务键、属性、SCD、来源 |
| `dwd_list.csv` | DWD 表、主题域、业务过程、粒度、字段角色、来源 |
| `field_mapping.csv` | 一行一条目标字段到来源字段的映射 |
| `dependency.csv` | DIM/DWD 加载依赖和顺序 |
| `model_design.md` | 人工审查用模型概要 |
| `validation_report.md` | PASS/WARN/FAIL 门禁结果 |

## 校验项

### 输入

- 是否解析到 DIM 和 DWD
- 必需文件和必要列是否存在
- 业务过程是否缺少主题域、粒度或粒度键
- 总线矩阵维度列是否映射到 DIM spec
- 总线矩阵正向维度是否匹配 DWD FK

### DIM

- 是否存在业务键和代理键
- 非日期维度是否包含属性
- 表级 SCD 策略是否正确
- SCD Type II 是否包含 `begin_date/end_date/is_active`

### DWD

- 是否存在明确粒度
- 非 `factless` DWD 是否包含度量
- 引用的 DIM 是否存在
- 维度业务键是否匹配 DIM 设计
- 粒度键、退化维度、低基数属性和业务时间是否保留

### 文件

- 必需 docs 是否存在
- 启用的 DDL/ETL 是否存在
- SQL 是否残留 `{{` 或 `}}`
- 字段映射和依赖清单是否覆盖主要目标字段

## 门禁等级

| 等级 | 含义 | 处理 |
|---|---|---|
| `PASS` | 无错误、无告警 | 可交付 |
| `WARN` | 有告警、无错误 | 审查并记录说明 |
| `FAIL` | 存在错误 | 修复后重新生成 |

`FAIL` 产物不得进入下游。`WARN` 必须附业务说明或处理计划。

## 执行命令

主流程自动生成校验报告：

```bash
python3 .claude/skills/cdm_modeling/scripts/main.py
```

独立校验：

```bash
python3 .claude/skills/cdm_modeling/scripts/validate_model.py output/cdm-modeling --write-report
```

校验脚本返回码：`0` 表示通过或仅告警，`1` 表示失败。

## 结构自测

```bash
python3 -m unittest discover -s .claude/skills/cdm_modeling/tests -v
git diff --check
```

自测使用真实 DWM 上游样例，并在临时目录生成完整 DIM/DWD、DDL、ETL 和 docs，避免污染仓库现有输出。

## 常见问题

- 输入字段混在备注中：改用结构化列。
- 文档承诺代码未生成的产物：统一文档和实现。
- 规则文件存在但未接入代码：删除或转为明确引用的 reference。
- SQL 看似完整但来源字段缺失：在校验报告中标记并阻断交付。
- 示例无法一条命令执行：更新测试或依赖说明。
