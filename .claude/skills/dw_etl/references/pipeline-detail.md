# DW ETL 流水线详细规格

## 1. 阶段一：metadata_parse（字段画像）

### 输入

源系统 DDL 文件（MySQL / Hive / 其他数据库的 CREATE TABLE 语句）。

### 执行

通过 `references/step1-ddl-parse.md` 中定义的方式解析 DDL，产出字段级元数据画像。

```bash
python .claude/skills/metadata_parse/scripts/step1-ddl-parse/export_all_tables.py
```

### 产出

| 文件 | 路径 | 内容 |
|------|------|------|
| `all_tables_metadata.xlsx` | `output/metadata_parse/` | 字段名、数据类型、主键、外键、外键引用、字段空值率、字段角色 |

### 验收

- Excel 文件生成成功
- 每张源表的所有字段均有记录
- `字段角色` 列有值（不为空）

---

## 2. 阶段二：ods_generator（ODS 层生成）

### 输入

| 文件 | 路径 |
|------|------|
| `all_tables_metadata.xlsx` | `output/metadata_parse/` |

### 执行

调用 `ods-generator` Skill：

```python
# Skill tool: ods-generator
```

或直接运行脚本：

```bash
python .claude/skills/ods-generator/scripts/generate_ods.py
```

### 产出

| 文件 | 路径 | 内容 |
|------|------|------|
| `all_tables_metadata_ods.xlsx` | `output/ods_generator/` | 原表名→新表名映射、主键、外键、DDL |
| `all_tables_metadata_ods.sql` | `output/ods_generator/` | Hive ODS 建表语句合集 |

### 命名规则

- ODS 表名：`ods_{数据源类型}_{数据库名}_{原表名}_df`
- 分区字段：`pt STRING COMMENT '分区日期'`
- 存储格式：ORC
- 全部新增 `etl_time` 字段

### 验收

- ODS 表数量 = 源表数量
- 每张表包含完整 `CREATE TABLE` 语句
- 分区字段、存储格式正确

---

## 3. 阶段三：dwm-matrix（总线矩阵）

### 输入

| 文件 | 路径 | 用途 |
|------|------|------|
| `all_tables_metadata.xlsx` | `output/metadata_parse/` | 字段角色、约束信息 |
| `all_tables_metadata_ods.xlsx` | `output/ods_generator/` | ODS 表清单 |

### 执行

调用 `dwm-matrix` Skill，该 Skill 内部编排两个子 Skill：

1. **dwm-business-process**：识别业务过程 → 声明粒度 → 确认事实 → 产出 DWD spec
2. **dwm-dimension**：提取维度引用 → 收敛一致性维度 → SCD 策略 → 产出 DIM spec
3. **dwm-matrix 自身**：验证 + 生成总线矩阵 Excel

```bash
# 验证+生成总线矩阵
python .claude/skills/dwm-matrix/scripts/write_bus_matrix.py \
  --business-process output/dwm-bus-matrix/dwm_bp_business_process.csv \
  --subject-area  output/dwm-bus-matrix/dwm_bp_subject_area.csv \
  --dim-registry  output/dwm-bus-matrix/dwm_dim_spec.csv \
  --dwd-fact-spec output/dwm-bus-matrix/dwm_dwd_fact_spec.csv \
  --field-metadata output/metadata_parse/all_tables_metadata.xlsx \
  --output        output/dwm-bus-matrix/dwm_bus_matrix.xlsx \
  --version v1.0
```

### 子阶段 3a：dwm-business-process

按 Kimball 四步法（第一、二、四步）：

1. 画表关系图（基于 FK 引用）
2. 按四项证据识别事实表（时间、度量、关联、增长）
3. 自底向上 + 自顶向下定义主题域（5~10 个）
4. 声明粒度（每个业务过程一句话 + 粒度键 + 唯一性校验）
5. 确定事实表类型（transaction / periodic_snapshot / accumulating_snapshot / factless）
6. 确认度量归属 → 产出 `dwm_dwd_fact_spec`

产出：

| 文件 | 内容 |
|------|------|
| `dwm_bp_business_process.csv` | 业务过程清单（粒度、类型） |
| `dwm_bp_subject_area.csv` | 主题域注册表 |
| `dwm_dwd_fact_spec.csv` | DWD 事实表字段级规格 |
| `dwm_dwd_join_spec.csv` | DWD ODS 关联关系 |

### 子阶段 3b：dwm-dimension

1. 技术字段排除（`tech_meta` 全部剔除）
2. 退化维度判定（交易凭证/业务单号，保留在事实表）
3. 提取维度外键引用
4. 收敛一致性维度（跨事实共享 → dim 表）
5. SCD 策略确认（SCD1/SCD2/SCD3）

产出：

| 文件 | 内容 |
|------|------|
| `dwm_dim_spec.csv` | 维度表字段级规格（含 SCD） |
| `dwm_dim_join_spec.csv` | DIM ODS 关联关系 |

### 子阶段 3c：矩阵验证 + Excel 生成

1. 粒度唯一性验证
2. JOIN 缺失率验证（≤ 1%）
3. 业务语义验证
4. 生成 `dwm_bus_matrix.xlsx`

### 验收

- 所有事实表有完整的业务过程名称、粒度声明、类型
- 粒度键唯一性通过
- 一致性维度跨事实口径一致
- 矩阵 Excel 生成成功

---

## 4. 阶段四：cdm_modeling（CDM 层建模）

### 输入

| 文件 | 路径 |
|------|------|
| `dwm_dwd_fact_spec.csv` | `output/dwm-bus-matrix/` |
| `dwm_dim_spec.csv` | `output/dwm-bus-matrix/` |
| `dwm_dwd_join_spec.csv` | `output/dwm-bus-matrix/` |
| `dwm_dim_join_spec.csv` | `output/dwm-bus-matrix/` |

### 执行

调用 `cdm_modeling` Skill：

- 读取 DIM spec → 生成 DIM DDL + INSERT OVERWRITE ETL
- 读取 DWD spec → 生成 DWD DDL + INSERT OVERWRITE ETL
- SCD 维度自动添加 `dw_start_date`/`dw_end_date`/`dw_is_current`
- 代理键生成（`row_number()` 窗口函数）

### 产出

```
output/cdm/
├── dim/
│   ├── ddl/          # DIM 建表语句
│   └── etl/          # DIM ETL 脚本
└── dwd/
    ├── ddl/          # DWD 建表语句
    └── etl/          # DWD ETL 脚本
```

### 验收

- DIM/DWD 建表语句语法正确
- ETL 逻辑与事实表/维度表规格一致
- SCD2 维度包含拉链字段

---

## 5. 阶段五：dws-designer（DWS 汇总层）

### 输入

依赖阶段三的总线矩阵和阶段四的 DIM/DWD 设计。

### 执行

调用 `dws-designer` Skill：

- 基于阿里 OneData + Kimball 维度建模理论
- 管理 `dws_list.csv`（支持初次创建与迭代更新）
- 严格遵循 `.claude/skills/dws-designer/reference/dws_design_guide.md` 规范
- DWS 层仅承载原子指标，严禁复合/派生指标

### 产出

```
output/dws/
├── dws_list.csv      # DWS 表清单
├── ddl/              # DWS 建表语句
└── etl/              # DWS ETL 脚本
```

### 验收

- DWS 表原子指标口径正确
- 无复合指标/派生指标混入
- 数量控制约束满足
- 维度属性冗余符合规范

---

## 6. 阶段间数据流

```
metadata_parse                 ods_generator
    │                                │
    ├─ all_tables_metadata.xlsx ─────┤
    │                                │
    │                     all_tables_metadata_ods.xlsx
    │                                │
    └────────────┬───────────────────┘
                 │
                 ▼
           dwm-matrix
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
 bp.csv      dim_spec    bus_matrix
 fact_spec   join_spec   .xlsx
    │            │            │
    └────────────┼────────────┘
                 │
                 ▼
           cdm_modeling
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
  DIM DDL     DIM ETL     DWD DDL   DWD ETL
    │            │            │
    └────────────┼────────────┘
                 │
                 ▼
           dws-designer
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
  DWS DDL     DWS ETL   dws_list.csv
```

---

## 7. 独立 Skill 索引

| Skill 名称 | SKILL.md 路径 | 职责 |
|-----------|--------------|------|
| metadata_parse | `.claude/skills/metadata_parse/` | 字段画像 |
| ods-generator | `.claude/skills/ods-generator/SKILL.md` | ODS DDL 生成 |
| dwm-business-process | `.claude/skills/dwm-business-process/SKILL.md` | 业务过程识别 |
| dwm-dimension | `.claude/skills/dwm-dimension/SKILL.md` | 维度确认 |
| dwm-matrix | `.claude/skills/dwm-matrix/SKILL.md` | 总线矩阵编排 |
| cdm-modeling | `.claude/skills/cdm_modeling/SKILL.md` | CDM 层建模 |
| dws-designer | `.claude/skills/dws-designer/SKILL.md` | DWS 汇总层 |

---

## 8. 常见问题

### Q: 上游元数据变化后如何处理？

从阶段 1 重新执行。如果仅 ODS 层以上变化，可从阶段 2 或阶段 3 开始。

### Q: 某阶段产出物已存在是否覆盖？

执行前检查 `output/` 目录，若同名文件存在则提示确认。用户可选择覆盖或跳过。

### Q: 阶段 3 验证不通过怎么办？

按回退表回退到对应阶段修正，不跳过验证。同一问题回退不超过 2 次。
