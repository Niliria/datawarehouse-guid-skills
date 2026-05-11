---
name: dwm-matrix
description: >-
  Use when the user asks to "构建总线矩阵", "数仓建模", "总线矩阵",
  "矩阵验证", "优先级发布", "DWD建设清单", "DIM建设清单",
  "bus matrix", "第一步", "第二步", "第三步", "第四步",
  or discusses data warehouse bus matrix construction, matrix assembly, validation, or delivery.
  This is the orchestrator that coordinates dwm-data-inventory, dwm-business-process, dwm-dimension.
version: 2.0.0
---

# 组装总线矩阵（编排 + 验证 + 交付）

## 定位

编排 dwm-data-inventory / dwm-business-process / dwm-dimension 三个 Skill，完成从数据源盘点到总线矩阵发布的全流程。同时负责矩阵验证和最终交付物合成。

基于《数据仓库工具箱》(Kimball) 四步法与《阿里巴巴大数据之路》分层实践。Kimball 负责"怎么建模是对的"，阿里分层负责"怎么工程化落地可持续"。

## 编排流程

```
dwm-data-inventory       数据盘点（ODS + 字段元数据 + 客观画像）
        ↓
dwm-business-process     选择业务过程 + 声明粒度 + 确认事实 (Kimball Step 1+2+4)
        ↓
dwm-dimension            确认维度 (Kimball Step 3)
        ↓
dwm-matrix               组装 + 验证 + 交付（本 Skill）
```

### 步骤映射

| 用户说 | 执行 Skill |
|--------|-----------|
| "第一步" / "数据盘点" / "ODS盘点" | → dwm-data-inventory |
| "第二步" / "识别业务过程" / "粒度声明" / "确认事实" / "度量归属" | → dwm-business-process |
| "第三步" / "确认维度" / "一致性维度" | → dwm-dimension |
| "第四步" / "矩阵验证" / "发布" | → dwm-matrix（验证 + 交付） |
| "构建总线矩阵" / "数仓建模" | → dwm-matrix 从第一步开始全流程 |

## 本 Skill 自身职责（验证 + 交付）

### 验证
- 粒度唯一性验证（每个业务过程）
- JOIN 验证（核心维度 JOIN 缺失率 ≤ 1%）
- 口径验证（一致性维度跨事实表口径一致）
- 应连未连检查

### 交付物合成
- DWD 事实表建设清单（字段级，含 ODS 溯源）
- DIM 维度表建设清单（字段级，含 ODS 溯源）
- 主题域清单
- 总线矩阵（published 版本）
- 优先级路线图

## 输入依赖

| 输入项 | 来源 Skill |
|--------|-----------|
| `dwm_inv_*` | dwm-data-inventory |
| `dwm_bp_*` | dwm-business-process |
| `dwm_dim_*` | dwm-dimension |

## 产出物

| 产出物 | 说明 | 输出路径 |
|--------|------|----------|
| `dwm_dwd_fact_spec` | **DWD 事实表建设清单** ★ | `output/dwm-bus-matrix/` |
| `dwm_dim_table_spec` | **DIM 维度表建设清单** ★ | `output/dwm-bus-matrix/` |
| `dwm_subject_area_summary` | **主题域清单** ★ | `output/dwm-bus-matrix/` |
| `dwm_bus_matrix.xlsx` | **总线矩阵** ★ | `output/dwm-bus-matrix/` |
| `dwm_matrix_check` | 矩阵验证报告 | `output/dwm-bus-matrix/assembly/` |
| `dwm_priority_roadmap` | 优先级路线图 | `output/dwm-bus-matrix/assembly/` |

★ = 最终交付物，路径与 `spec-to-dwd-dim-job` Skill 对齐

## 回退规则

| 当前步骤 | 回退目标 | 触发条件 |
|---------|---------|---------|
| dwm-business-process | dwm-data-inventory | 字段画像有误导致表角色判断错误 |
| dwm-dimension | dwm-data-inventory | 外键画像有误导致维度关联错误 |
| dwm-matrix | dwm-dimension | 应连未连或维度口径不一致 |
| dwm-matrix | dwm-business-process | 聚合结果违反业务常���或度量归属有误 |

回退原则：最小回退、影响评估、变更审批、防循环（同一问题不超过 2 次）。

## 术语统一

| 用语 | 含义 |
|-----|------|
| 主题域 | 业务过程按相似性归组后的分类 |
| 主题域编码 | 2~3 个大写字母（如 `TRD`），用于表命名 |

禁用"业务域""数据域"，统一收敛为"主题域"。

## CSV 工具与矩阵生成

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

```bash
python .claude/skills/dwm-matrix/scripts/write_bus_matrix.py \
  --business-process output/dwm-bus-matrix/business-process/dwm_bp_business_process.csv \
  --subject-area  output/dwm-bus-matrix/business-process/dwm_bp_subject_area.csv \
  --dim-registry  output/dwm-bus-matrix/dimension/dwm_dim_registry.csv \
  --field-profile output/dwm-bus-matrix/inventory/dwm_inv_field_profile.csv \
  --output        output/dwm-bus-matrix/dwm_bus_matrix.xlsx \
  --version v1.0
```

## 代码编写规范

涉及以下场景时，通过 `use context7` 获取最新文档再编写代码：
- 编写矩阵验证 SQL（JOIN 缺失率、粒度唯一性）
- 编写 DWD/DIM spec 合成 Python 脚本
- 安装或调用 openpyxl 生成 Excel 文件

## 详细规格

Read `references/matrix-assembly.md` for validation procedures, deliverable schemas, priority roadmap, methodology foundations, and rollback rules.
