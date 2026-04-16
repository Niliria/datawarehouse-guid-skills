---
name: dwm-business-process
description: >-
  Use when the user asks to "识别业务过程", "业务过程识别", "声明粒度", "粒度声明",
  "定义主题域", "主题域划分", "表角色判定", "select business process", "declare grain",
  or needs to identify business processes, define subject areas, and declare grain for each process.
version: 1.0.0
---

# 选择业务过程 + 声明粒度（Kimball Step 1+2）

## 定位

对应 Kimball 四步法的**前两步**：选择业务过程（总线矩阵的行）并声明每个过程的粒度。不声明粒度的业务过程识别没有意义。

同步完成主题域定义与归组。

## 职责边界

**做什么**：
- 判定表角色（`fact` / `dimension` / `config` / `exclude`）
- 识别业务过程并标准命名
- 定义主题域（先自底向上聚类，再自顶向下校验）
- 声明粒度（一句话 + 粒度键 + 唯一性校验）
- 接口数据无主键时通过画像降级发现业务键和外键

**不做什么**：
- 不做字段画像（→ dwm-data-inventory）
- 不判度量归属（→ dwm-fact）
- 不提取维度引用（→ dwm-dimension）

## 输入依赖

| 输入项 | 来源 Skill | 用途 |
|--------|-----------|------|
| `dwm_inv_field_profile` | dwm-data-inventory | 字段角色画像，用于画表关系图 |
| `dwm_inv_field_registry` | dwm-data-inventory | 约束信息（PK/UK/FK），连线主依据 |
| `dwm_inv_ods_inventory` | dwm-data-inventory | ODS 表清单与同步模式 |

## 产出物

| 产出物 | 说明 | 输出路径 |
|--------|------|----------|
| `dwm_bp_table_profile` | 表角色画像表 | `output/dwm-bus-matrix/business-process/` |
| `dwm_bp_subject_area` | 主题域注册表 | `output/dwm-bus-matrix/business-process/` |

## CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

## 代码编写规范

涉及以下场景时，通过 `use context7` 获取最新文档再编写代码：
- 编写唯一率分析 SQL（发现天然业务键）
- 编写 JOIN 命中率分析 SQL（发现外键关系）
- 编写粒度唯一性校验 SQL

## 详细规格

Read `references/business-process.md` for table role classification, subject area design, grain declaration, and acceptance criteria.
