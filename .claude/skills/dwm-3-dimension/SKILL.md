---
name: dwm-3-dimension
description: >-
  Use when the user asks to "确认维度", "维度确定", "维度提取", "一致性维度",
  "SCD策略", "退化维度判定", "维度注册", "identify dimensions", "conformed dimensions",
  or needs to extract dimension references from fact tables and register conformed dimensions.
version: 1.0.0
---

# ③ 确认维度（Kimball Step 3）

## 定位

对应 Kimball 四步法的**第三步**：确认维度。从每个业务过程中提取维度引用，收敛一致性维度，确认 SCD 策略。

## 职责边界

**做什么**：
- 提取维度外键引用（每个业务过程 → 关联哪些维度）
- 识别退化维度（事实表中的交易凭证/业务单号）
- 识别低基数离散属性候选
- 收敛一致性维度（跨事实表共享的维度 → 建 DIM 表）
- 确认 SCD 策略（SCD1/SCD2/SCD3）

**不做什么**：
- 不判事实表类型（→ ④ dwm-4-fact）
- 不判度量归属（→ ④ dwm-4-fact）
- 不做字段画像（→ ① dwm-1-data-inventory）

## 输入依赖

| 输入项 | 来源 Skill | 用途 |
|--------|-----------|------|
| `dwm_bp_table_profile WHERE table_role='fact'` | ② | 业务过程清单与粒度声明 |
| `dwm_bp_table_profile WHERE table_role='dimension'` | ② | 维度候选表与粒度键 |
| `dwm_inv_field_profile` | ① | 字段角色画像（外键、业务键等） |
| `dwm_bp_subject_area` | ② | 主题域定义 |

## 产出物

| 产出物 | 说明 | 输出路径 |
|--------|------|----------|
| `dwm_dim_fact_ref` | 维度引用底稿（每个事实表 → 关联哪些维度） | `output/dwm-bus-matrix/dimension/` |
| `dwm_dim_registry` | 一致性维度注册表（需建 DIM 表的维度） | `output/dwm-bus-matrix/dimension/` |

## CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

## 代码编写规范

涉及以下场景时，通过 `use context7` 获取最新文档再编写代码：
- 编写一致性维度校验 SQL（命名、口径、值域、JOIN 命中率）
- 编写 SCD 维度加工脚本（追踪历史变化）
- 编写批量维度引用提取脚本

## 详细规格

Read `references/dimension.md` for dimension extraction rules, conformed dimension criteria, SCD strategy, degenerate dimension rules, and acceptance criteria.
