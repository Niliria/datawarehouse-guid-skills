---
name: dwm-bus-matrix
description: >-
  This skill should be used when the user asks to "构建总线矩阵", "数仓建模",
  "第一步", "第二步", "第三步", "第四步", "第五步",
  "ODS盘点", "字段打标签", "字段标注", "业务过程识别", "粒度声明",
  "维度确定", "事实确定", "矩阵验证", "优先级发布",
  "数据源接入", "一致性维度", "bus matrix",
  or discusses data warehouse bus matrix construction methodology based on Kimball and Alibaba approaches.
version: 1.0.0
---

# 数仓总线矩阵构建 — 五步操作法

基于《数据仓库工具箱》(Kimball) 四步法与《阿里巴巴大数据之路》分层实践，通过五个结构化步骤完成从数据源接入到总线矩阵发布的全流程。Kimball 负责"怎么建模是对的"，阿里分层负责"怎么工程化落地可持续"。

## 术语统一

| 用语 | 含义 |
|-----|------|
| 主题域 | 业务过程按相似性归组后的分类，对齐 Kimball Subject Area 与阿里主题域 |
| 主题域编码 | 2~3 个大写字母（如 `TRD` 交易域、`USR` 用户域），用于 DWD/DWS/ADS 表命名 |

禁用"业务域""数据域"，统一收敛为"主题域"。

## 五步流程总览

| 步骤 | 核心目标 | 关键产出 | Reference |
|-----|---------|---------|-----------|
| 第一步 | 数据源登记 + ODS 盘点 | `dwm_s1_source_registry` / `dwm_s1_ods_inventory` / `dwm_s1_field_registry` | `references/step1-ods-inventory.md` |
| 第二步 | 逐字段语义标签化 + fact_candidate 初判 | `dwm_s2_field_tag` | `references/step2-field-tagging.md` |
| 第三步 | 业务过程识别 + 主题域定义 + 粒度声明 | `dwm_s3_table_profile` / `dwm_s3_subject_area` | `references/step3-business-process.md` |
| 第四步 | 事实与维度确定 + 总线矩阵草稿 | `dwm_s4_fact_metric` / `dwm_s4_fact_dim_ref` / `dwm_s4_dim_registry` / `dwm_bus_matrix`（工作底稿） | `references/step4-dimension-fact.md` |
| 第五步 | 矩阵验证 + 最终交付物发布 | `dwm_dwd_fact_spec` / `dwm_dim_table_spec` / `dwm_subject_area_summary` / `dwm_s5_matrix_check` / `dwm_s5_priority_roadmap` | `references/step5-matrix-validation.md` |

流程主线：第一步 → 第二步 → 第三步 → 第四步 → 第五步 → 建设阶段（DIM → DWD → DWS → ADS）。

## 15 张产出物一览

所有产出物统一命名 `dwm_s{步骤号}_{语义英文名}`，输出为数据库表或 CSV。

| 步骤 | 产出物 | 说明 | 性质 |
|:---:|--------|------|------|
| S1 | `dwm_s1_source_registry` | 数据源注册表 | 基础数据 |
| S1 | `dwm_s1_ods_inventory` | ODS 表清单 | 基础数据 |
| S1 | `dwm_s1_field_registry` | 源字段清单 | 基础数据 |
| S2 | `dwm_s2_field_tag` | 字段标注结果 | 基础数据 |
| S3 | `dwm_s3_table_profile` | 表角色画像 | 基础数据 |
| S3 | `dwm_s3_subject_area` | 主题域注册表 | 基础数据 |
| S4 | `dwm_s4_fact_metric` | 度量归属底稿 | 工作底稿 |
| S4 | `dwm_s4_fact_dim_ref` | 维度引用底稿 | 工作底稿 |
| S4 | `dwm_s4_dim_registry` | 一致性维度底稿 | 工作底稿 |
| S4 | `dwm_bus_matrix` | 总线矩阵草稿（含 version + status） | 工作底稿 |
| S5 | `dwm_dwd_fact_spec` | **DWD 事实表建设清单**（字段级，含 ODS 溯源） | **最终交付物** |
| S5 | `dwm_dim_table_spec` | **DIM 维度表建设清单**（字段级，含 ODS 溯源） | **最终交付物** |
| S5 | `dwm_subject_area_summary` | **主题域清单**（含业务过程数与表数统计） | **最终交付物** |
| S5 | `dwm_s5_matrix_check` | 矩阵验证报告 | 过程产出 |
| S5 | `dwm_s5_priority_roadmap` | 优先级路线图 | 规划产出 |

## 执行规则

### 跨步骤回写约定

后续步骤可修正前步产出（如第四步回写第三步 `fact_type`）：
- 每步验收区分"当步必须完成"与"下游回填后复验"
- 回写字段当步允许为空，标记为"待回填"
- 回填完成后须通过原步骤复验检查

### 回退触发条件

| 当前步骤 | 回退目标 | 触发条件 |
|---------|---------|---------|
| 第三步 | 第二步 | `fact_candidate` 初判有误 |
| 第四步 | 第二步 | 字段标签错误导致口径冲突 |
| 第四步 | 第三步 | 粒度声明有误 |
| 第五步 | 第四步 | 应连未连或维度口径不一致 |
| 第五步 | 第三步 | 聚合结果违反业务常识 |
| 建设阶段 | 第四步 | DWD 聚合差异 > 0.1% |
| 建设阶段 | 第二步 | 生产 JOIN miss_rate 远高于采样 |

回退原则：最小回退、影响评估、变更审批、防循环（同一问题不超过 2 次）、变更记录到 `dwm_s5_matrix_check`。

### 批量执行策略

按业务优先级分批（首批 20~30 张核心表），每批次独立通过门禁即可进入后续步骤。门禁基于批次覆盖率 100%，非全量阻塞。

## 各步执行指引

### 第一步：数据源接入与 ODS 盘点

登记数据源技术属性与元数据完整度（完整/部分/缺失），盘点 ODS 表清单与同步策略，采集源系统字段约束信息。元数据完整度决定第二步标注模式（标准/降级/快速）。

Read `references/step1-ods-inventory.md` for field definitions, collection methods, and acceptance criteria.

### 第二步：逐字段语义标签化

使用 15 个固定标签（10 核心 + 5 扩展）为每个 ODS 字段赋予语义。执行两遍扫描：第一遍跳过退化维度（Q5），完成 `fact_candidate` 初判后，第二遍对事实候选表执行 Q5。关键阈值：唯一率 ≥ 99.9%、外键缺失率 ≤ 1%、低基数上限 ≤ 50。

Read `references/step2-field-tagging.md` for the complete decision tree, threshold system, and output template.

### 第三步：业务过程识别与粒度声明

通过表关系网识别业务过程（总线矩阵的行），定义主题域（先自底向上聚类，再自顶向下校验），声明粒度并做唯一性校验。接口数据无主键时通过画像降级发现业务键和外键。

Read `references/step3-business-process.md` for degradation strategies, output definitions, and derived queries.

### 第四步：事实与维度确定 + 总线矩阵草稿

先确认事实表类型（驱动度量归属逻辑），再提取维度外键并收敛一致性维度（含 SCD 策略），最后填充总线矩阵草稿。本步产出 4 张工作底稿，第五步合成为最终交付物。

Read `references/step4-dimension-fact.md` for fact type classification, dimension registry schema, and matrix structure.

### 第五步：矩阵验证与最终交付物发布

验证矩阵正确性（JOIN/粒度/口径），合成四项最终交付物：总线矩阵（发布版）、DWD 事实表建设清单（字段级，含 ODS 溯源）、DIM 维度表建设清单（字段级，含 ODS 溯源）、主题域清单。优先级路线图作为附带规划产出。

Read `references/step5-matrix-validation.md` for validation procedures, deliverable schemas, and priority roadmap.

## 输出约定

各步中间产出写入 `output/dwm-bus-matrix/stepN/` 目录，4 个最终交付物直接写入 `output/dwm-bus-matrix/` 根目录：

```
output/
└── dwm-bus-matrix/
    ├── dwm_bus_matrix.xlsx              ★ 最终交付物
    ├── dwm_dwd_fact_spec.csv            ★ 最终交付物
    ├── dwm_dim_table_spec.csv           ★ 最终交付物
    ├── dwm_subject_area_summary.csv     ★ 最终交付物
    ├── step1/
    │   ├── dwm_s1_source_registry.csv
    │   ├── dwm_s1_ods_inventory.csv
    │   └── dwm_s1_field_registry.csv
    ├── step2/
    │   └── dwm_s2_field_tag.csv
    ├── step3/
    │   ├── dwm_s3_table_profile.csv
    │   └── dwm_s3_subject_area.csv
    ├── step4/
    │   ├── dwm_s4_fact_dim_ref.csv
    │   ├── dwm_s4_fact_metric.csv
    │   └── dwm_s4_dim_registry.csv
    └── step5/
        ├── dwm_s5_matrix_check.csv
        └── dwm_s5_priority_roadmap.csv
```

### CSV 格式要求

- 编码：UTF-8 with BOM（Excel 兼容）
- 分隔符：逗号
- 首行为表头（与 references 中字段定义表的 `字段名` 列一致）
- 空值写空字符串，不写 `NULL`
- 含逗号或换行的字段值用双引号包裹

### CSV 写入方式

使用 `scripts/write_csv.py` 写入 CSV 文件。将数据组装为 JSON 数组，通过 stdin 传入：

```bash
echo '[{"source_code":"my001","source_type":"MySQL","table_count":45}]' \
  | python .claude/skills/dwm-bus-matrix/scripts/write_csv.py output/dwm-bus-matrix/step1/dwm_s1_source_registry.csv
```

### CSV 读取方式

使用 `scripts/read_csv.py` 读取前步产出。支持过滤、选列、计数、去重：

```bash
# 读取第一步全部字段清单
python .claude/skills/dwm-bus-matrix/scripts/read_csv.py output/dwm-bus-matrix/step1/dwm_s1_field_registry.csv

# 第二步读取第一步的外键字段（按条件过滤）
python .claude/skills/dwm-bus-matrix/scripts/read_csv.py output/dwm-bus-matrix/step1/dwm_s1_field_registry.csv \
  --where "constraint_type=FK" --select "src_table_name,src_column_name,ref_table,ref_column"

# 第三步读取第二步的外键标注
python .claude/skills/dwm-bus-matrix/scripts/read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv \
  --where "core_tag=外键" --where "review_status=approved"

# 统计数量
python .claude/skills/dwm-bus-matrix/scripts/read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv \
  --where "core_tag=外键" --count

# 查看某列的所有取值
python .claude/skills/dwm-bus-matrix/scripts/read_csv.py output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv \
  --distinct "core_tag"
```

两个脚本自动处理 UTF-8 BOM，数据格式统一为 JSON（写入 JSON→CSV，读取 CSV→JSON）。

### 批量处理脚本

当数据量大（>50 行）需编写 Python 脚本批量处理时，通过 `sys.path` 导入现有工具函数，禁止重写 CSV 读写逻辑：

```python
import sys, os
sys.path.insert(0, ".claude/skills/dwm-bus-matrix/scripts")
from read_csv import read_csv
from write_csv import write_csv

# 读取前步产出
fields = read_csv("output/dwm-bus-matrix/step1/dwm_s1_field_registry.csv")

# 处理业务逻辑...
results = [...]

# 写入当步产出
write_csv("output/dwm-bus-matrix/step2/dwm_s2_field_tag.csv", results)
```

规则：
- 禁止在批量脚本中直接使用 `csv.DictReader` / `csv.DictWriter`，统一走 `read_csv()` / `write_csv()` 确保 BOM 编码、空值处理一致
- 批量脚本从项目根目录执行（`python script.py`）

### 总线矩阵生成方式

使用 `scripts/write_bus_matrix.py` 从 step3/step4 CSV 产出生成交叉表 xlsx（需 `pip install openpyxl`）：

```bash
python .claude/skills/dwm-bus-matrix/scripts/write_bus_matrix.py \
  --table-profile output/dwm-bus-matrix/step3/dwm_s3_table_profile.csv \
  --subject-area  output/dwm-bus-matrix/step3/dwm_s3_subject_area.csv \
  --fact-dim-ref  output/dwm-bus-matrix/step4/dwm_s4_fact_dim_ref.csv \
  --dim-registry  output/dwm-bus-matrix/step4/dwm_s4_dim_registry.csv \
  --output        output/dwm-bus-matrix/dwm_bus_matrix.xlsx \
  --version v1.0
```

### 执行规则

1. 每步完成后立即写文件，不等全流程结束
2. 同一步骤重新执行时覆盖已有文件
3. 矩阵类输出（`dwm_bus_matrix`）使用 Excel 格式（`.xlsx`），便于二维交叉展示
4. 目录不存在时自动创建
5. 写入后用 Git 追踪变化

## 输出格式规范

- **命名规范**：`dwm_s{步骤号}_{语义英文名}`
- **结构化产出**：CSV 文件落盘到 `output/dwm-bus-matrix/stepN/`
- **矩阵类产出**：Excel 表格（`.xlsx`），通过 `version` + `status` 管理生命周期

## 详细规格

For methodology foundations, rollback rules, and output format specifications:
- **`references/dwm-bus-matrix.md`** — Methodology, rollback rules, output format standards

For complete field definitions, decision trees, SQL templates, and acceptance criteria per step:
- **`references/step1-ods-inventory.md`** — Data source registration and ODS inventory
- **`references/step2-field-tagging.md`** — Field semantic tagging (15 tags, decision tree, thresholds)
- **`references/step3-business-process.md`** — Business process identification and grain declaration
- **`references/step4-dimension-fact.md`** — Dimension/fact determination and bus matrix construction
- **`references/step5-matrix-validation.md`** — Matrix validation and priority release
