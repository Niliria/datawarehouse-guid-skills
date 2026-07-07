---
name: cdm-modeling
description: >-
  当用户提出“CDM建模”“DIM设计”“DWD设计”“根据总线矩阵生成模型”“生成维度表和事实表”
  “生成建表语句”“生成ETL”“SCD策略”或“拉链表”时应使用此 Skill。
  读取 dwm-business-process、dwm-dimension、dwm-matrix 的标准交付物，生成 CDM 层 DIM/DWD 模型及校验产物。
version: 1.4.0
---

# CDM 建模 Skill

读取上游 DWM 标准化产物，生成 CDM 层 DIM/DWD 数据模型、DDL、ETL、字段映射、依赖清单和校验报告。

## 使用边界

用于“业务过程、维度和总线矩阵已经完成”的建设阶段。不得重新解析原始 ODS DDL，不得绕过上游文档猜测业务过程、粒度或维度关系。

遵循 OneData 分层口径：

- DIM 独立维护一致性维度、业务键、代理键和 SCD 生命周期。
- DWD 保持业务过程原子粒度，关联 DIM 只获取代理键，不展开维度描述属性。
- DWS/ADS 承接汇总、宽表和应用服务，不由本 Skill 生成。

## 上游输入契约

将以下文件作为权威输入：

| 文件 | 上游 | 必需性 | 用途 |
|---|---|---|---|
| `dwm_dim_spec.csv` | dwm-dimension | 必需 | DIM 字段、业务键、属性、SCD、来源字段 |
| `dwm_dwd_fact_spec.csv` | dwm-business-process | 必需 | DWD 粒度键、FK、描述字段、度量、业务时间 |
| `dwm_bus_matrix.xlsx` | dwm-matrix | 必需 | 事实表与一致性维度的权威关联关系 |
| `dwm_bp_business_process.csv` | dwm-business-process | 推荐 | 补充并校验业务过程、粒度键和事实类型 |
| `dwm_bp_subject_area.csv` | dwm-business-process | 推荐 | 校验主题域编码 |
| `dwm_dim_join_spec.csv` | dwm-dimension | 可选 | DIM 多 ODS 来源及关联条件 |
| `dwm_dwd_join_spec.csv` | dwm-business-process | 可选 | DWD 多 ODS 来源及关联条件 |

统一从 `output/dwm-bus-matrix/` 读取这些文件。沿用 dwm-shared 的 UTF-8 BOM CSV 与 XLSX 首行表头约定。

### 最新字段名称

DIM spec 使用：`维度表名`、`维度中文名称`、`维度描述`、`来源ODS表`、`SCD策略`、`是否一致性维度`、`跨事实表共享范围`、`字段名`、`字段中文说明`、`字段角色`、`SCD类型`、`来源ODS字段`、`ODS数据类型`、`字段排序`。

DWD spec 使用：`DWD表名`、`事实表中文名称`、`主题域编码`、`业务过程标准名`、`事实表类型`、`粒度声明`、`字段名`、`字段中文说明`、`字段角色`、`来源ODS表`、`来源ODS字段`、`ODS数据类型`、`度量类型`、`聚合建议`、`度量单位`、`是否派生`、`派生逻辑`、`字段排序`。

## 五步流程

| 步骤 | 核心目标 | 关键产出 | Reference |
|---|---|---|---|
| 1 | 读取并校验全部上游契约 | 统一建模上下文、输入告警 | `references/upstream-contract.md` |
| 2 | 生成 DIM 设计 | 业务键、属性、SCD 策略 | `references/dim-modeling.md` |
| 3 | 生成 DWD 设计 | 粒度键、维度代理键、明细字段、度量 | `references/dwd-modeling.md` |
| 4 | 渲染 DDL、ETL 与清单 | SQL、映射、依赖、模型清单 | `references/validation.md` |
| 5 | 执行模型门禁 | `validation_report.md` | `references/validation.md` |

## 维度关系解析

按以下优先级确定 DWD 到 DIM 的映射：

1. 兼容读取 DWD spec 中显式的 `关联DIM表`、`关联DIM业务键`。
2. 以 `dwm_bus_matrix.xlsx` 中的 `Y/✓` 单元格确定事实表应关联的维度。
3. 使用 DWD `字段角色=fk` 的字段名或来源字段，与 DIM `pk/bk` 字段精确匹配。
4. 无法唯一匹配时写入校验告警，不静默猜测。

保留 DWD spec 中的 `grain_key`、`degenerate_dim`、`low_card_attr`、`measure`、`business_time`，不得只生成度量而丢失明细追踪字段。

## 输出约定

默认写入 `output/cdm-modeling/`：

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

## 关键规则

- 优先使用上游物理表名、字段名、粒度和业务语义，不在模板中重新推断。
- 使用 DIM 表级 `SCD策略` 决定整体 SCD 类型；使用字段级 `SCD类型` 决定跟踪属性。
- 非 `factless` DWD 必须至少包含一个度量；缺失时生成告警。
- 总线矩阵标记的每个维度必须匹配到 DWD FK 和已生成 DIM，否则校验失败。
- 仅在上游确实缺少业务键时使用 `{entity}_id`，并记录告警。
- 生成后必须执行产物门禁校验。

## 详细资料

- `references/upstream-contract.md`：上游文件、字段、配置和解析优先级
- `references/dim-modeling.md`：DIM 字段、SCD、DDL/ETL 和验收规则
- `references/dwd-modeling.md`：DWD 粒度、维度映射、字段和度量规则
- `references/validation.md`：产物结构、强制门禁、反模式和自测方法

## 脚本

- `scripts/main.py`：主入口
- `scripts/parse_upstream_outputs.py`：DWM 全量输入契约解析
- `scripts/generate_dim.py`：DIM 设计和 DDL
- `scripts/generate_dwd.py`：DWD 设计和 DDL
- `scripts/generate_etl.py`：ETL 生成
- `scripts/validate_model.py`：产物门禁
