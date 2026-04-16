# Skill 完整性审查报告：dwm-4-fact & dwm-5-bus-matrix

---

## Skill 1：dwm-4-fact（确认事实）

### 1. 结构审查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| SKILL.md 存在 | ✅ | 60行，结构完整 |
| references/ 目录 | ✅ | 含 `fact.md`（138行） |
| scripts/ 目录 | ❌ **不存在** | 无自有脚本 |
| context7/MCP 引用 | ❌ **无** | 全文无 `context7`、`mcp__` 相关引用 |

### 2. SKILL.md 内容分析

**做得好的：**
- 清晰的 Kimball Step 4 定位说明
- 职责边界明确（做什么 / 不做什么）
- 输入依赖表完整（依赖 ①② 的产出物）
- 产出物定义：`dwm_fct_metric` + `dwm_fct_type`，路径 `output/dwm-bus-matrix/fact/`
- CSV 工具引用指向 `dwm-shared/scripts`

**CSV 工具路径：**
```python
sys.path.insert(0, ".claude/skills/dwm-shared/scripts")
```
→ ✅ 指向 `dwm-shared/scripts/`（该目录存在，含 `read_csv.py` + `write_csv.py`，与 `dwm-bus-matrix/scripts/` 完全一致）

### 3. 与原始参考文档对比（step4-dimension-fact.md 的 fact 部分）

原始 `step4-dimension-fact.md` 是一个**合并文档**，涵盖：
- §2.1 确定事实表类型 → fact 部分
- §2.2 确定度量 → fact 部分
- §2.3 提取维度引用 → **dimension 部分**（应由 dwm-3-dimension 负责）
- §2.4 收敛一致性维度 → **dimension 部分**
- §2.5 组装总线矩阵草稿 → **bus-matrix 部分**（应由 dwm-5-bus-matrix 负责）

**方法论完整性（fact 部分）：**

| 原始参考中的 fact 方法论 | dwm-4-fact 覆盖 | 状态 |
|-------------------------|-----------------|------|
| 事实表类型判定（4种） | ✅ references/fact.md §2.1 | 完整 |
| 判定规则（4条） | ✅ | 完整 |
| 度量确定流程（6步） | ✅ references/fact.md §2.2 | 完整 |
| 度量可加性类型（3种） | ✅ | 完整 |
| 度量与事实表类型匹配表 | ✅ | 完整 |
| 派生事实识别 | ✅ | 完整 |
| 度量可加性校验规则 | ✅ references/fact.md §2.3 | **原始无，sub-skill 增加了**（加分项）|
| `dwm_fct_type` schema | ✅ | 完整 |
| `dwm_fct_metric` schema | ✅ | 完整 |
| 验收标准 | ✅ 5条 | 完整 |
| 与下一步衔接 | ✅ | 完整 |

### 4. 命名体系差异（⚠️ 关键问题）

| 对象 | 原始参考 (step4) | dwm-4-fact sub-skill | 影响 |
|------|-------------------|---------------------|------|
| 度量底稿 | `dwm_s4_fact_metric` | `dwm_fct_metric` | ⚠️ 命名不一致 |
| 事实类型 | （回写 `dwm_s3_table_profile`） | `dwm_fct_type` (新增独立表) | ✅ 合理改进 |
| 输入-业务过程 | `dwm_s3_table_profile` | `dwm_bp_table_profile` | ⚠️ 命名不一致 |
| 输入-字段画像 | `dwm_s2_field_tag` | `dwm_inv_field_profile` | ⚠️ 命名不一致 |
| 输入-字段注册 | `dwm_s1_field_registry` | `dwm_inv_field_registry` | ⚠️ 命名不一致 |

**判定**：sub-skill 使用了 `dwm_{skill缩写}_` 前缀体系（`inv_`, `bp_`, `fct_`, `dim_`），而原始参考使用 `dwm_s{step}_` 前缀体系。**两套命名并存会导致跨 skill 引用混乱。** 但只要 5 个 sub-skill 内部一致，这属于有意识的重命名。需确认 dwm-1/2/3/5 是否也统一用了新命名。

### 5. 缺失项汇总

| 缺失项 | 严重性 | 说明 |
|--------|--------|------|
| 无 context7/MCP 引用 | ⚠️ 中 | SQL 生成场景（如粒度验证 SQL、聚合校验 SQL）可受益于 context7 查 SparkSQL 语法 |
| 无自有 scripts/ | ℹ️ 低 | 当前步骤无需自有脚本，仅依赖 shared CSV 工具即可 |
| 度量可加性校验无 SQL 模板 | ⚠️ 中 | 原始参考也没有，但实操中需要可执行的校验 SQL |

### 6. Skill 1 评分：⭐⭐⭐⭐ (4/5)

方法论完��，甚至比原始参考增加了可加性校验规则。主要扣分点：命名体系差异需与其他 skill 统一确认。

---

## Skill 2：dwm-5-bus-matrix（组装总线矩阵）

### 1. 结构审查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| SKILL.md 存在 | ✅ | 126行，内容丰富 |
| references/ 目录 | ❌ **空目录** | 目录存在但无任何文件！ |
| scripts/ 目录 | ✅ | 含 `write_bus_matrix.py`（246行） |
| context7/MCP 引用 | ❌ **无** | 全文无 `context7`、`mcp__` 相关引用 |

### 2. SKILL.md 内容分析

**做得好的：**
- 编排流程图清晰（①→②→③④→⑤）
- 步骤映射表完整（用户说什么 → 执行哪个 skill）
- 验证职责明确（4类验证）
- 交付物清单完整（6项）
- 回退规则表完整
- 术语统一声明（禁用"业务域""数据域"）
- CSV 工具路径正确指向 `dwm-shared/scripts`
- write_bus_matrix.py 调用示例完整

**关键问题：**
```
## 详细规格
Read `references/matrix-assembly.md` for validation procedures, deliverable schemas, 
priority roadmap, methodology foundations, and rollback rules.
```
→ ❌ **`references/matrix-assembly.md` 文件不存在！** 这是最严重的问题。

### 3. 与原始参考文档对比（step5-matrix-validation.md）

原始 `step5-matrix-validation.md` 是一份 300 行的详尽文档，包含：

| 原始参考内容 | SKILL.md 覆盖 | references/ 覆盖 | 总体状态 |
|-------------|--------------|-----------------|---------|
| §2.1 矩阵验证（4类验证 + SQL 模板） | 仅列名（4项） | ❌ 无 | ❌ **严重缺失** |
| §2.2 DWD 事实表合成流程（5步） | 仅列名 | ❌ 无 | ❌ **严重缺失** |
| §2.3 DIM 维度表合成流程（5步） | 仅列名 | ❌ 无 | ❌ **严重缺失** |
| §2.4 主题域清单合成（7步） | 仅列名 | ❌ 无 | ❌ **严重缺失** |
| §2.5 建设优先级规划 | 仅列名 | ❌ 无 | ❌ **严重缺失** |
| §3.1 `dwm_s5_matrix_check` schema（15字段） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §3.2 `dwm_dwd_fact_spec` schema（18字段） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §3.3 `dwm_dim_table_spec` schema（12字段） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §3.4 `dwm_subject_area_summary` schema（12字段） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §3.5 `dwm_s5_priority_roadmap` schema（11字段） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §3.6 总线矩阵发布流程 | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| §4 验收标准（8条） | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| 附录 A 建设阶段反馈机制 | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| 粒度唯一性验证 SQL 模板 | ❌ 无 | ❌ 无 | ❌ **严重缺失** |
| DWD 表名生成规则 | ❌ 无 | ❌ 无 | ❌ **严重缺失** |

**结论：SKILL.md 只是一个「目录/索引」，所有详细规格本应在 `references/matrix-assembly.md` 中，但该文件完全缺失。这意味着 LLM 执行此 skill 时无法获得任何字段级 schema 定义、验证 SQL 模板、合成流程细节。**

### 4. 产出物 Schema 定义缺失详情

以下 5 个核心交付物的字段级 schema 在 sub-skill 中完全缺失（原始参考中有详尽定义）：

#### `dwm_dwd_fact_spec`（18个字段）
- dwd_table_name, subject_area_code, bp_standard_name, fact_type, grain_statement
- dwd_column_name, dwd_column_comment, column_role, ods_table_name, ods_column_name
- ods_data_type, ref_dim_table, agg_suggest, unit, is_derived, derived_logic
- sort_order, remark, updated_at
→ **全部缺失**

#### `dwm_dim_table_spec`（12个字段）
- dim_table_name, dimension_name, dim_column_name, dim_column_comment
- column_role, scd_type, ods_table_name, ods_column_name, ods_data_type
- sort_order, remark, updated_at
→ **全部缺失**

#### `dwm_subject_area_summary`（12个字段）
- subject_area_code, subject_area_name_cn/en, subject_area_desc
- bp_count, dwd_table_count, dim_table_count, ods_table_count
- bp_list, dwd_table_list, dim_table_list, updated_at
→ **全部缺失**

#### `dwm_matrix_check`（原始名 `dwm_s5_matrix_check`，15个字段）
→ **全部缺失**

#### `dwm_priority_roadmap`（原始名 `dwm_s5_priority_roadmap`，11个字段）
→ **全部缺失**

### 5. 脚本引用分析

#### write_bus_matrix.py（dwm-5-bus-matrix 本地副本 vs dwm-bus-matrix 共享副本）

| 对比项 | dwm-5-bus-matrix/scripts/ | dwm-bus-matrix/scripts/ |
|--------|--------------------------|------------------------|
| 文件大小 | 9272 bytes | 9230 bytes |
| 唯一差异 | `sys.path.insert(0, "../../dwm-shared/scripts")` | `sys.path.insert(0, os.path.dirname(...))` |
| read_csv 来源 | → `dwm-shared/scripts/read_csv.py` | → 同目录 `read_csv.py` |

**问题**：
1. ⚠️ 存在两份几乎相同的 `write_bus_matrix.py`（违反 DRY）
2. ⚠️ `dwm-5-bus-matrix` 本地副本通过 `../../dwm-shared/scripts` 引用 `read_csv`，而 `dwm-bus-matrix` 版本通过同目录引用
3. 本地副本的 docstring 中的 usage 路径是 `step3/step4`（`dwm_s3_*` / `dwm_s4_*`），但 SKILL.md 中的调用示例路径是 `business-process/` 和 `dimension/`：

```bash
# SKILL.md 中的调用：
--table-profile output/dwm-bus-matrix/business-process/dwm_bp_table_profile.csv
--fact-dim-ref  output/dwm-bus-matrix/dimension/dwm_dim_fact_ref.csv

# 脚本 docstring 中的路径：
--table-profile output/dwm-bus-matrix/step3/dwm_s3_table_profile.csv
--fact-dim-ref  output/dwm-bus-matrix/step4/dwm_s4_fact_dim_ref.csv
```
→ ❌ **路径和文件名双重不一致**

### 6. 命名体系差异

| 对象 | 原始参考 (step5) | dwm-5-bus-matrix SKILL.md | 影响 |
|------|------------------|--------------------------|------|
| 矩阵验证报告 | `dwm_s5_matrix_check` | `dwm_matrix_check` | ⚠️ |
| 优先级路线图 | `dwm_s5_priority_roadmap` | `dwm_priority_roadmap` | ⚠️ |
| DWD spec | `dwm_dwd_fact_spec` | `dwm_dwd_fact_spec` | ✅ 一致 |
| DIM spec | `dwm_dim_table_spec` | `dwm_dim_table_spec` | ✅ 一致 |
| 主题域清单 | `dwm_subject_area_summary` | `dwm_subject_area_summary` | ✅ 一致 |
| 输入引用 | `dwm_s4_*`, `dwm_s3_*` | `dwm_fct_*`, `dwm_bp_*`, `dwm_dim_*`, `dwm_inv_*` | ⚠️ |

### 7. Skill 2 评分：⭐⭐ (2/5)

SKILL.md 作为编排索引尚可，但核心方法论（验证流程、合成流程、所有 schema 定义、验收标准、SQL 模板）全部缺失。原因明确：`references/matrix-assembly.md` 文件从未创建。

---

## 共享基础设施分析

### dwm-shared/scripts/ vs dwm-bus-matrix/scripts/

| 文件 | dwm-shared/scripts/ | dwm-bus-matrix/scripts/ | 差异 |
|------|---------------------|------------------------|------|
| read_csv.py | ✅ 存在 | ✅ 存在 | **完全一致**（diff 无输出）|
| write_csv.py | ✅ 存在 | ✅ 存在 | **完全一致**（diff 无输出）|
| write_bus_matrix.py | ❌ 不存在 | ✅ 存在 | — |

**问题**：
1. `read_csv.py` 和 `write_csv.py` 存在于**两个位置**的相同副本 → 违反 single source of truth
2. Sub-skills（dwm-4-fact, dwm-5-bus-matrix）都指向 `dwm-shared/scripts/`，这是正确的
3. `dwm-bus-matrix/scripts/write_bus_matrix.py` 引用同目录的 `read_csv.py`（自包含），而 `dwm-5-bus-matrix/scripts/write_bus_matrix.py` 引用 `dwm-shared/scripts/read_csv.py`（依赖外部）

### 脚本引用路径一致性

| Skill | CSV 工具引用路径 | 实际目标 | 状态 |
|-------|-----------------|---------|------|
| dwm-4-fact SKILL.md | `dwm-shared/scripts` | dwm-shared/scripts/{read,write}_csv.py | ✅ |
| dwm-5-bus-matrix SKILL.md | `dwm-shared/scripts` | dwm-shared/scripts/{read,write}_csv.py | ✅ |
| dwm-5-bus-matrix/scripts/write_bus_matrix.py | `../../dwm-shared/scripts` | 相对路径解析到 dwm-shared/scripts/ | ✅ |
| dwm-bus-matrix/scripts/write_bus_matrix.py | 同目录 | dwm-bus-matrix/scripts/read_csv.py | ✅（自包含）|

---

## 总结与修复建议

### 🔴 紧急（阻塞执行）

1. **创建 `dwm-5-bus-matrix/references/matrix-assembly.md`**
   - 将 `step5-matrix-validation.md` 的内容适配后放入
   - 包含：5 个产出物的完整字段级 schema、4 类验证的详细流程与 SQL 模板、合成流程（DWD/DIM/主题域）、验收标准 8 条、建设阶段反馈机制
   - 命名从 `dwm_s5_*` 体系转为 `dwm_{category}_*` 体系

2. **修复 SKILL.md 中 write_bus_matrix.py 的调用参数路径**
   - 当前 SKILL.md 写的是 `business-process/dwm_bp_table_profile.csv`
   - 脚本 docstring 写的是 `step3/dwm_s3_table_profile.csv`
   - 需统一为一套命名+路径

### 🟡 重要（影响质量）

3. **消除 write_bus_matrix.py 双副本**
   - 保留 `dwm-5-bus-matrix/scripts/write_bus_matrix.py` 作为唯一权威版
   - 或移至 `dwm-shared/scripts/` 统一管理
   - `dwm-bus-matrix/scripts/write_bus_matrix.py` 标记为 deprecated 或删除

4. **跨 skill 命名体系统一确认**
   - 确认所有 5 个 sub-skill 均已从 `dwm_s{N}_` 前缀迁移到 `dwm_{category}_` 前缀
   - 若未统一，在某处维护一张映射表

5. **为关键操作步骤增加 SQL 模板**
   - dwm-4-fact：度量可加性校验 SQL
   - dwm-5-bus-matrix：粒度唯一性验证 SQL、JOIN 缺失率验证 SQL、口径验证 SQL

### 🟢 建议（提升体验）

6. **考虑添加 context7 引用**
   - 在生成 SparkSQL DDL/DML 时，用 `context7` 查最新语法
   - 在 SKILL.md 的 CSV 工具段落下方加上 SQL 生成指引

7. **dwm-4-fact 考虑添加决策树**
   - 事实表类型判定可画成 if/else 决策树而非表格
   - 提升 LLM 执行准确性
