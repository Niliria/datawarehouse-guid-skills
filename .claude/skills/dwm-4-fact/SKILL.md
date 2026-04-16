---
name: dwm-4-fact
description: >-
  Use when the user asks to "确认事实", "事实确定", "度量归属", "度量确认",
  "事实表类型", "派生度量", "identify facts", "determine measures",
  or needs to classify fact table types and attribute measures to business processes.
version: 1.0.0
---

# ④ 确认事实（Kimball Step 4）

## 定位

对应 Kimball 四步法的**第四步**：确认事实。先确定事实表类型（驱动度量可加性校验规则），再将度量归属到对应业务过程。

**为什么先事实后维度不对？** 实际上③和④可以并行，但④的度量可加性校验依赖事实表类型。Kimball 原文中"确定维度"先于"确定事实"，但两者在实践中常交替进行。本框架将维度独立为③是因为维度引用不依赖事实表类型，而度量归属依赖。

## 职责边界

**做什么**：
- 确定事实表类型（transaction / periodic_snapshot / accumulating_snapshot / factless）
- 将度量归属到对应事实表
- 校验度量可加性与事实表类型匹配
- 识别派生度量（如 利润 = 收入 - 成本）

**不做什么**：
- 不提取维度引用（→ ③ dwm-3-dimension）
- 不做字段画像（→ ① dwm-1-data-inventory）
- 不识别业务过程（→ ② dwm-2-business-process）

## 输入依赖

| 输入项 | 来源 Skill | 用途 |
|--------|-----------|------|
| `dwm_bp_table_profile WHERE table_role='fact'` | ② | 业务过程清单与粒度声明 |
| `dwm_inv_field_profile` | ① | 字段角色画像（数值型字段 → 度量候选） |
| `dwm_inv_field_registry` | ① | 字段类型信息 |

## 产出物

| 产出物 | 说明 | 输出路径 |
|--------|------|----------|
| `dwm_fct_metric` | 度量归属底稿 | `output/dwm-bus-matrix/fact/` |
| `dwm_fct_type` | 事实表类型确认表 | `output/dwm-bus-matrix/fact/` |

`dwm_fct_type` 的 `fact_type` 和 `fact_type_evidence` 同时回写 `dwm_bp_table_profile`，保持兼容。

## CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

## 代码编写规范

涉及以下场景时，通过 `use context7` 获取最新文档再编写代码：
- 编写度量可加性校验 SQL（聚合跨维度求和验证）
- 编写事实表类型判定脚本（时间、度量、行数分析）

## 详细规格

Read `references/fact.md` for fact type classification, measure attribution rules, derived measure handling, and acceptance criteria.
