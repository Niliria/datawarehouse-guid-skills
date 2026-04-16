# Skill 完整性审查报告

## 审查对象

| # | Skill 目录 | 对照参考文件 |
|---|-----------|------------|
| 1 | `dwm-2-business-process/` | `dwm-bus-matrix/references/step3-business-process.md` (213行) |
| 2 | `dwm-3-dimension/` | `dwm-bus-matrix/references/step4-dimension-fact.md` 维度部分 (248行) |

---

## Skill 1: dwm-2-business-process（业务过程识别+粒度声明）

### 1.1 结构盘点

| 检查项 | 状态 | 详情 |
|--------|------|------|
| SKILL.md 存在？ | ✅ 存在 | 59行，结构完整 |
| references/ 目录？ | ⚠️ **空目录** | 目录已创建但 **无任何文件** |
| scripts/ 目录？ | ❌ 不存在 | 无自有脚本（引用 dwm-shared 的 CSV 工具） |
| Context7/MCP 工具提及？ | ❌ 无 | SKILL.md 中未提及任何 MCP 工具或 Context7 |

### 1.2 SKILL.md 内容评估

**已涵盖（骨架完整）：**
- ✅ 定位说明（Kimball Step 1+2）
- ✅ 职责边界（做什么/不做什么）— 清晰隔离了与①③④的边界
- ✅ 输入依赖表（3个输入项 + 来源 Skill）
- ✅ 产出物表（2个：`dwm_bp_table_profile`, `dwm_bp_subject_area`）
- ✅ CSV 工具引用（`dwm-shared/scripts`）
- ✅ 末尾有 `Read references/business-process.md` 指令

**关键缺失：**
- ❌ **references/business-process.md 不存在** — SKILL.md 最后一行指向 `references/business-process.md`，但该文件根本不存在！这是一个**断链**。

### 1.3 与原始参考 step3-business-process.md 的差异分析

| 参考文件中的内容模块 | SKILL.md 中是否体现？ | 缺失严重度 |
|--------------------|--------------------|-----------|
| §1 输入（5类过滤条件 + 接口数据降级策略） | ⚠️ 仅概述，降级策略仅一句话 | 🔴 高 |
| §1 降级策略的 SQL 模板（唯一率分析、JOIN 命中率） | ❌ 完全缺失 | 🔴 高 |
| §2.1 画表关系图（4步操作方法） | ❌ 完全缺失 | 🟡 中 |
| §2.2 识别业务过程（四类证据评估 + 判定规则） | ⚠️ 仅列举判定值，无决策树 | 🔴 高 |
| §2.2 主题域定义方法（自底向上+自顶向下） | ⚠️ 仅一句话概述 | 🟡 中 |
| §2.3 声明粒度（5步流程 + 唯一性校验） | ⚠️ 仅 4 个要点概述 | 🔴 高 |
| §3.1 `dwm_s3_table_profile` 完整字段定义（18字段） | ❌ 完全缺失 | 🔴 高 |
| §3.2 `dwm_s3_subject_area` 完整字段定义（8字段） | ❌ 完全缺失 | 🔴 高 |
| §3.3 表关系图可视化 SQL | ❌ 完全缺失 | 🟡 中 |
| §3.4 派生查询 SQL（3个） | ❌ 完全缺失 | 🟡 中 |
| §4 验收标准（9条当步 + 2条回写复验） | ❌ 完全缺失 | 🔴 高 |
| §5 与下一步衔接（5条） | ❌ 完全缺失 | 🟡 中 |

### 1.4 Skill 1 结论

> **SKILL.md 是一个合格的"目录页/索引页"，但它指向的详细规格文件（references/business-process.md）完全缺失。**
>
> 当前状态：**功能残缺，无法独立工作**。AI 执行此 Skill 时，会尝试 `Read references/business-process.md` 但读不到任何内容，退化为仅靠 SKILL.md 的 59 行概述来工作——缺失字段定义、决策树、SQL 模板、验收标准等全部细节。

---

## Skill 2: dwm-3-dimension（确认维度）

### 2.1 结构盘点

| 检查项 | 状态 | 详情 |
|--------|------|------|
| SKILL.md 存在？ | ✅ 存在 | 58行，结构完整 |
| references/ 目录？ | ⚠️ **空目录** | 目录已创建但 **无任何文件** |
| scripts/ 目录？ | ❌ 不存在 | 无自有脚本（引用 dwm-shared 的 CSV 工具） |
| Context7/MCP 工具提及？ | ❌ 无 | SKILL.md 中未提及任何 MCP 工具或 Context7 |

### 2.2 SKILL.md 内容评估

**已涵盖（骨架完整）：**
- ✅ 定位说明（Kimball Step 3）
- ✅ 职责边界（做什么/不做什么）— 5个"做"（维度外键、退化维度、低基数、一致性维度、SCD策略）
- ✅ 输入依赖表（4个输入项）
- ✅ 产出物表（2个：`dwm_dim_fact_ref`, `dwm_dim_registry`）
- ✅ CSV 工具引用
- ✅ 末尾有 `Read references/dimension.md` 指令

**关键缺失：**
- ❌ **references/dimension.md 不存在** — 又是一个**断链**。

### 2.3 与原始参考 step4-dimension-fact.md（维度部分）的差异分析

step4-dimension-fact.md 是一个 **合体文件**（事实+维度+总线矩阵），其中维度相关部分为 §2.3~§2.4 和 §3.2~§3.3。

| 参考文件中的维度内容模块 | SKILL.md 中是否体现？ | 缺失严重度 |
|------------------------|--------------------|-----------|
| §2.3 提取维度引用（6步详细流程） | ⚠️ 仅列举5个要点概述 | 🔴 高 |
| §2.3 硬门禁规则（技术属性/技术时间剔除） | ❌ 完全缺失 | 🔴 高 |
| §2.3 退化维度判定规则（core_tag='退化维度'） | ⚠️ 仅一行概述 | 🟡 中 |
| §2.3 低基数离散属性候选提取 | ⚠️ 仅一行概述 | 🟡 中 |
| §2.3 必选维度 + 缺失容忍策略 | ❌ 完全缺失 | 🟡 中 |
| §2.4 收敛一致性维度（6步详细流程） | ⚠️ 仅一行概述 | 🔴 高 |
| §2.4 一致性检查规则（命名/口径/编码/值域/JOIN 命中率） | ❌ 完全缺失 | 🔴 高 |
| §2.4 SCD 策略确认（SCD1/2/3 决策规则 + scd_columns 格式） | ⚠️ 仅标题级概述 | 🔴 高 |
| §3.2 `dwm_s4_fact_dim_ref` 完整字段定义（12字段） | ❌ 完全缺失 | 🔴 高 |
| §3.3 `dwm_s4_dim_registry` 完整字段定义（14字段） | ❌ 完全缺失 | 🔴 高 |
| §3.5 派生查询 SQL（技术属性剔除、factless、复杂属性） | ❌ 完全缺失 | 🟡 中 |
| §4 验收标准（8条） | ❌ 完全缺失 | 🔴 高 |
| §5 与下一步衔接 | ❌ 完全缺失 | 🟡 中 |

### 2.4 Skill 2 结论

> **与 Skill 1 完全相同的问题模式：SKILL.md 是合格的索引页，但 references/dimension.md 断链。**
>
> 当前状态：**功能残缺，无法独立工作**。

---

## 横向对比：各 Skill 的完整度

| Skill | SKILL.md | references/ 有文件？ | scripts/ | 可独立工作？ |
|-------|----------|-------------------|----------|------------|
| dwm-1-data-inventory | ✅ 63行 | ❌ 空目录 | ❌ | ❌ 同样断链 |
| **dwm-2-business-process** | ✅ 59行 | ❌ 空目录 | ❌ | ❌ 断链 |
| **dwm-3-dimension** | ✅ 58行 | ❌ 空目录 | ❌ | ❌ 断链 |
| dwm-4-fact | ✅ 60行 | ✅ fact.md (138行) | ❌ | ✅ **唯一完整的** |
| dwm-5-bus-matrix | ✅ | ❌ | ✅ write_bus_matrix.py | ⚠️ 部分 |

> **发现：dwm-4-fact 是唯一一个 references/ 目录下有实际文件的拆分 Skill。** 其他 4 个 Skill（①②③⑤）的 references/ 都是空目录。

---

## 缺失清单总结

### Skill 1 (dwm-2-business-process) 需要创建的文件

**`references/business-process.md`** — 应包含以下内容（从 step3-business-process.md 适配）：

1. **输入过滤条件表**（5类 core_tag 过滤条件）
2. **接口数据无主键降级策略**（4种场景 + 操作方法）
3. **降级策略 SQL 模板**（唯一率分析、JOIN 命中率分析）
4. **画表关系图流程**（4步 + 连线规则）
5. **表角色判定决策树**（四类证据：时间/度量/关联/增长 → fact/dimension/config/exclude）
6. **主题域定义方法**（自底向上聚类 + 自顶向下校验）
7. **粒度声明流程**（5步 + 唯一性校验 SQL）
8. **产出物字段定义**：
   - `dwm_bp_table_profile`（18字段完整规格）
   - `dwm_bp_subject_area`（8字段完整规格 + 设计原则）
9. **表关系图可视化 SQL**
10. **派生查询 SQL**（3个）
11. **验收标准**（9条当步 + 2条回写复验）
12. **与下一步衔接**（5条衔接规则）

### Skill 2 (dwm-3-dimension) 需要创建的文件

**`references/dimension.md`** — 应包含以下内容（从 step4-dimension-fact.md 的维度部分适配）：

1. **维度提取流程**（§2.3 的 6 步详细流程）
2. **硬门禁规则**（技术属性/技术时间全部剔除）
3. **退化维度判定规则**（core_tag='退化维度' 的提取逻辑）
4. **低基数离散属性候选提取**
5. **必选维度与缺失容忍策略**（如匿名用户填充 UNKNOWN）
6. **一致性维度收敛流程**（§2.4 的 6 步流程）
7. **一致性检查规则**（命名/口径/编码/值域/JOIN 命中率）
8. **SCD 策略决策规则**（SCD1/2/3 判定 + scd_columns 格式 `SCD2:col1,col2;SCD1:col3`）
9. **产出物字段定义**：
   - `dwm_dim_fact_ref`（12字段完整规格）
   - `dwm_dim_registry`（14字段完整规格）
10. **派生查询 SQL**（技术属性剔除清单、复杂属性清单）
11. **验收标准**（8条）
12. **与下一步衔接**

### 两个 Skill 共同缺失

- ❌ 无 Context7 / MCP 工具使用指引（所有 Skill 均无）
- ❌ 无 SQL 生成模板（需在 references 中补充）
- ❌ 无 scripts/（当前依赖 dwm-shared，结构上可接受，但如果有特定校验脚本则需补充）

---

## 建议优先级

| 优先级 | 行动 | 原因 |
|--------|------|------|
| 🔴 P0 | 创建 `dwm-2-business-process/references/business-process.md` | 断链，Skill 无法工作 |
| 🔴 P0 | 创建 `dwm-3-dimension/references/dimension.md` | 断链，Skill 无法工作 |
| 🟡 P1 | 同步创建 `dwm-1-data-inventory/references/data-inventory.md` | 同样断链 |
| 🟢 P2 | 考虑是否需要在各 Skill 中添加 Context7/MCP 工具使用指引 | 当前所有 Skill 均无 |

> **核心问题**：拆分 Skill 时只创建了 SKILL.md（索引页）和空 references/ 目录，但忘记把原始参考文件的对应内容拆分填入。dwm-4-fact 是唯一完成了这一步的。
