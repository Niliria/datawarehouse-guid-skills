# 上游输入契约

读取 dwm-business-process、dwm-dimension、dwm-matrix 的标准交付物，形成 DIM/DWD 生成所需的统一建模上下文。沿用 dwm-shared 的 UTF-8 BOM CSV 和 XLSX 首行表头约定。

## 输入文件

| 配置项 | 文件 | 必需性 | 作用 |
|---|---|---|---|
| `business_process_file` | `dwm_bp_business_process.csv` | 推荐 | 业务过程、粒度键、事实类型 |
| `subject_area_file` | `dwm_bp_subject_area.csv` | 推荐 | 主题域主数据 |
| `dim_spec_file` | `dwm_dim_spec.csv` | 必需 | DIM 字段级建设规格 |
| `dwd_fact_spec_file` | `dwm_dwd_fact_spec.csv` | 必需 | DWD 字段级建设规格 |
| `bus_matrix_file` | `dwm_bus_matrix.xlsx` | 必需 | 事实与一致性维度关系 |
| `dim_join_spec_file` | `dwm_dim_join_spec.csv` | 可选 | DIM ODS 关联关系 |
| `dwd_join_spec_file` | `dwm_dwd_join_spec.csv` | 可选 | DWD ODS 关联关系 |

默认从 `output/dwm-bus-matrix/` 读取全部文件。

## 配置示例

```yaml
input:
  business_process_file: "../../../output/dwm-bus-matrix/dwm_bp_business_process.csv"
  subject_area_file: "../../../output/dwm-bus-matrix/dwm_bp_subject_area.csv"
  dim_spec_file: "../../../output/dwm-bus-matrix/dwm_dim_spec.csv"
  dwd_fact_spec_file: "../../../output/dwm-bus-matrix/dwm_dwd_fact_spec.csv"
  bus_matrix_file: "../../../output/dwm-bus-matrix/dwm_bus_matrix.xlsx"
  dim_join_spec_file: "../../../output/dwm-bus-matrix/dwm_dim_join_spec.csv"
  dwd_join_spec_file: "../../../output/dwm-bus-matrix/dwm_dwd_join_spec.csv"

output:
  target_dir: "../../../output/cdm-modeling"

modeling:
  default_scd_type: 1
  default_fact_type: transaction
  generate_ddl: true
  generate_etl: true
```

## 必要字段

### DIM spec

至少读取：

- `维度表名`
- `字段名`
- `字段角色`
- `来源ODS表`
- `来源ODS字段`
- `ODS数据类型`

同时保留 `维度中文名称`、`维度描述`、`SCD策略`、`是否一致性维度`、`跨事实表共享范围`、`SCD类型`、`字段排序`。

### DWD spec

至少读取：

- `DWD表名`
- `业务过程标准名`
- `字段名`
- `字段角色`
- `来源ODS表`
- `来源ODS字段`
- `ODS数据类型`

同时保留 `事实表中文名称`、`主题域编码`、`事实表类型`、`粒度声明`、`度量类型`、`聚合建议`、`度量单位`、`是否派生`、`派生逻辑`、`字段排序`。

### 总线矩阵

至少读取固定列 `业务过程代码` 和 `事实表名称`。将其余列视为维度列，并使用 DIM spec 的 `维度中文名称` 解析列头。将 `Y/YES/TRUE/1/✓/√` 识别为已关联。

## 解析规则

1. 按 `维度表名` 聚合 DIM 字段，使用 `pk/bk` 作为业务键，使用 `attribute` 作为维度属性。
2. 优先使用表级 `SCD策略` 确定 DIM 类型，保留字段级 `SCD类型` 识别跟踪属性。
3. 按 `DWD表名` 聚合 DWD 字段，完整保留 `grain_key`、`fk`、`degenerate_dim`、`low_card_attr`、`measure` 和 `business_time`。
4. 以总线矩阵确定事实表应关联的维度，再用 DWD FK 与 DIM `pk/bk` 匹配具体字段。
5. 优先使用显式 `关联DIM表/关联DIM业务键`，兼容旧版或增强版输入。
6. 保留 join spec 中的主表、从表、关联方式与关联条件。
7. 使用业务过程清单补充缺失的粒度键、粒度声明和事实类型。
8. 使用主题域注册表校验主题域编码。
9. 兼容 `DIM表名/DIM字段名/DWD字段名/ODS字段数据类型` 等旧列名，但新产物统一采用当前 DWM 列名。

## 统一上下文

```text
processes: DWD 业务过程、粒度键、全部字段、维度引用、度量、来源关联
dimensions: DIM 表、业务键、属性、表级/字段级 SCD、来源关联
business_processes: 业务过程原始清单
subject_areas: 主题域原始清单
matrix_links: 事实表/业务过程到 DIM 表的映射
ods_tables: DIM/DWD 字段血缘索引
warnings: 输入缺失、歧义和冲突告警
```

## 输入验收

1. 至少解析一个 DIM 和一个 DWD。
2. 确认每个 DIM 存在业务键。
3. 确认每个 DWD 存在业务过程、主题域、粒度声明和粒度键。
4. 确认每个总线矩阵正向标记均映射到 DIM 和 DWD FK。
5. 确认每个非 `factless` DWD 至少包含一个度量。
6. 将全部输入告警写入 `validation_report.md`。

## 执行命令

```bash
python3 .claude/skills/cdm_modeling/scripts/main.py
python3 .claude/skills/cdm_modeling/scripts/main.py --config path/to/skill_config.yaml
```
