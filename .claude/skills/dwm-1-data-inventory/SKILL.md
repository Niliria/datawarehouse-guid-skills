---
name: dwm-1-data-inventory
description: >-
  Use when the user asks to "数据盘点", "ODS盘点", "数据源接入", "字段采集",
  "字段画像", "元数据采集", "源系统登记", "field profiling",
  or needs to register data sources, inventory ODS tables, and profile field metadata.
version: 1.0.0
---

# ① 数据盘点（ODS + 字段元数据 + 客观画像）

## 定位

完成"有哪些数据源"、"源里有哪些表/字段"和"每个字段的客观画像"三件事，为后续建模步骤提供输入基座。

对应 Kimball 四步法的**前置准备**——建模开始前必须先清楚有什么数据。

## 职责边界

**做什么**：
- 数据源登记（技术属性 + 元数据完整度评估）
- ODS 表清单盘点（同步策略、分区、行数）
- 源字段元数据采集（类型、约束、注释）
- 字段客观画像（7 种客观角色 + 补充画像属性）

**不做什么**：
- 不判度量可加性（→ ④ dwm-4-fact）
- 不判退化维度（→ ③ dwm-3-dimension）
- 不判 fact_candidate（→ ② dwm-2-business-process 直接判表角色）
- 不定义主题域（→ ② dwm-2-business-process）

## 输入

| 输入项 | 说明 |
|--------|------|
| 系统接入清单 | 数据库/接口/文件等数据源清单 |
| 连接参数与访问凭证 | 数据库连接串、API token、文件路径等 |
| 目标 ODS 命名规则 | 数据库/表/字段命名规范 |
| 每张 ODS 表的字段元数据 | 字段名、类型、注释 |
| 小样本数据（建议最近 7~30 天） | 用于画像统计 |

## 产出物

| 产出物 | 说明 | 输出路径 |
|--------|------|----------|
| `dwm_inv_source_registry` | 数据源注册表 | `output/dwm-bus-matrix/inventory/` |
| `dwm_inv_ods_inventory` | ODS 表清单 | `output/dwm-bus-matrix/inventory/` |
| `dwm_inv_field_registry` | 源字段清单 | `output/dwm-bus-matrix/inventory/` |
| `dwm_inv_field_profile` | 字段客观画像 | `output/dwm-bus-matrix/inventory/` |

## CSV 工具

```python
import sys
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
from read_csv import read_csv
from write_csv import write_csv
```

## 代码编写规范

涉及以下场景时，通过 `use context7` 获取最新文档再编写代码：
- 编写数据库元数据采集 SQL（MySQL / PostgreSQL / Hive / Spark 等）
- 编写字段画像统计 SQL（唯一率、空值率、基数统计）
- 编写批量处理 Python 脚本（pandas / pyspark 等）

## 详细规格

Read `references/data-inventory.md` for field definitions, profiling decision tree, thresholds, and acceptance criteria.
