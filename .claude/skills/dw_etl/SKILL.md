---
name: dw-etl
description: >-
  This skill should be used when the user asks to "数据仓库建设", "数仓建设", "全流程建模",
  "端到端数仓", "DW ETL", "数据仓库全流程", "一键建模",
  or requests end-to-end data warehouse modeling from source DDL to DWS layer.
  Orchestrates the full pipeline: metadata_parse → ods_generator → dwm-matrix → cdm_modeling → dws-designer.
version: 1.0.0
---

# DW ETL 全流程编排

## 定位

串联五阶段数据仓库建设流水线，从源系统 DDL 解析到 DWS 汇总层产出，一次性完成端到端建模。

## 流水线总览

```
源系统 DDL
    │
    ▼
[1] metadata_parse    字段画像 + 角色标注
    │
    ├── output/metadata_parse/all_tables_metadata.xlsx
    │
    ▼
[2] ods_generator     ODS 层 DDL 生成
    │
    ├── output/ods_generator/all_tables_metadata_ods.xlsx
    │
    ▼
[3] dwm-matrix        总线矩阵（业务过程 + 维度 + 交叉验证）
    │
    ├── output/dwm-bus-matrix/dwm_bus_matrix.xlsx
    ├── output/dwm-bus-matrix/dwm_dwd_fact_spec.csv
    ├── output/dwm-bus-matrix/dwm_dim_spec.csv
    │
    ▼
[4] cdm_modeling      DIM + DWD 建表 + ETL
    │
    ▼
[5] dws-designer      DWS 汇总层设计
```

## 阶段说明

| 阶段 | Skill | 核心产出 | 依赖上游 |
|------|-------|---------|---------|
| 1 | metadata_parse | 字段画像 Excel | 源系统 DDL |
| 2 | ods_generator | ODS DDL + 表清单 | 阶段 1 |
| 3 | dwm-matrix | 总线矩阵 + DIM/DWD 规格 | 阶段 1 + 阶段 2 |
| 4 | cdm_modeling | DIM/DWD DDL + ETL | 阶段 3 |
| 5 | dws-designer | DWS DDL + ETL | 阶段 3 + 阶段 4 |

## 执行策略

### 全量执行（默认）

```bash
# 按阶段顺序依次调用各 Skill，前一步通过验收后自动进入下一步
```

每个阶段完成后校验产出物完整性，通过后继续。失败时根据回退规则处理。

### 增量执行

```bash
# 指定起始阶段，从该阶段开始执行至阶段 5
--from <stage>
```

适用场景：上游元数据未变，仅需重跑部分阶段。

### 单阶段执行

```bash
# 仅执行指定阶段
--stage <1-5>
```

适用场景：调试或单独修正某一阶段。

## 验收门禁

每个阶段通过后检查：

| 阶段 | 验收项 | 判定标准 |
|------|--------|---------|
| 1 | 字段画像完整 | 所有表字段均有角色标注、空值率 |
| 2 | ODS 表覆盖 | ODS 表数量 = 源表数量 |
| 3 | 粒度唯一性 | 所有事实表粒度键唯一 |
| 3 | 维度 JOIN 缺失率 | ≤ 1% |
| 4 | DIM/DWD 建表语句可执行 | 语法校验通过 |
| 5 | DWS 原子指标口径 | 无复合/派生指标混入 |

## 回退规则

| 阶段 | 失败回退目标 | 触发条件 |
|------|------------|---------|
| 3 | 阶段 1 | 字段画像有误导致表角色判断错误 |
| 3 | 阶段 2 | ODS 表映射错误 |
| 4 | 阶段 3 | 总线矩阵维度口径不一致 |
| 5 | 阶段 3 | DWS 聚合结果违反业务常识 |

回退原则：最小回退，同一问题不超过 2 次。

## 产出物总览

```
output/
├── metadata_parse/
│   └── all_tables_metadata.xlsx       # 字段画像
├── ods_generator/
│   ├── all_tables_metadata_ods.xlsx    # ODS 表清单
│   └── all_tables_metadata_ods.sql     # ODS DDL
├── dwm-bus-matrix/
│   ├── dwm_bp_subject_area.csv         # 主题域
│   ├── dwm_bp_business_process.csv     # 业务过程
│   ├── dwm_dwd_fact_spec.csv           # DWD 事实表规格
│   ├── dwm_dwd_join_spec.csv           # DWD ODS 关联
│   ├── dwm_dim_spec.csv               # 维度表规格
│   ├── dwm_dim_join_spec.csv           # DIM ODS 关联
│   └── dwm_bus_matrix.xlsx            # 总线矩阵
├── cdm/
│   ├── dim/                            # DIM DDL + ETL
│   └── dwd/                            # DWD DDL + ETL
└── dws/
    ├── dws_list.csv                    # DWS 表清单
    ├── ddl/                            # DWS DDL
    └── etl/                            # DWS ETL
```

## 详细规格

Read `references/pipeline-detail.md` for step-by-step execution details, individual skill interfaces, input/output specifications, and rollback procedures.

## 代码编写规范

- 每个阶段的 Skill 调用使用 `Skill` tool
- 阶段间传递通过共享 `output/` 目录下的文件
- 不重复实现各阶段内部逻辑，仅编排
- 所有 CSV 读写通过 `dwm-shared/scripts/` 下的工具
