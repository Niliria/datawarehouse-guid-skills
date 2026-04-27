-- ========================================
-- DIM 维度表 ETL SQL 模板
-- ========================================
-- 用于生成 DIM 维度表的加载脚本
-- 支持 SCD Type I 和 Type II 处理

{% if scd_type == 1 %}
-- ========== SCD Type I: 覆盖更新 ==========
-- 新的维度值直接覆盖旧值，不保留历史
-- 适用于变化频繁且不需要追踪历史的维度

INSERT OVERWRITE TABLE {{ table_name }} PARTITION (pt='${PT_DATE}')
SELECT
    ROW_NUMBER() OVER (ORDER BY {{ business_key }}) AS {{ entity }}_sk,  -- 生成代理键
    {% for field in fields %}
    {{ field.name }},
    {% endfor %}
    CURRENT_TIMESTAMP() AS etl_insert_time,
    CURRENT_TIMESTAMP() AS etl_update_time
FROM dws_{{ domain }}_{{ entity }}_di
WHERE pt = '${PT_DATE}'
    AND is_valid = 1;


{% elif scd_type == 2 %}
-- ========== SCD Type II: 拉链表(完整历史) ==========
-- 维度值变化时生成新记录，旧记录标记为失效
-- 记录开始日期和结束日期，支持时间维度分析

-- 步骤1：临时表 - 承载最新的DWS数据
DROP TABLE IF EXISTS tmp_dim_{{ entity }}_new;
CREATE TABLE tmp_dim_{{ entity }}_new AS
SELECT
    {{ business_key }},
    {% for field in fields %}
    {{ field.name }},
    {% endfor %}
    CURRENT_TIMESTAMP() AS etl_time
FROM dws_{{ domain }}_{{ entity }}_di
WHERE pt = '${PT_DATE}'
    AND is_valid = 1;

-- 步骤2：识别变化的记录
-- 旧记录存在但新值不同 = 发生了变化
DROP TABLE IF EXISTS tmp_dim_{{ entity }}_changed;
CREATE TABLE tmp_dim_{{ entity }}_changed AS
SELECT
    old.{{ entity }}_sk,
    old.{{ business_key }},
    {% for field in fields %}
    old.{{ field.name }},
    {% endfor %}
    '${PT_DATE}' AS end_date,    -- 旧记录失效时间
    0 AS is_active
FROM {{ table_name }} old
INNER JOIN tmp_dim_{{ entity }}_new new
    ON old.{{ business_key }} = new.{{ business_key }}
    AND old.is_active = 1
WHERE
    -- 至少一个属性发生变化
    {% for field in fields %}
    NVL(old.{{ field.name }}, '') != NVL(new.{{ field.name }}, '')
    {% if not loop.last %} OR {% endif %}
    {% endfor %};

-- 步骤3：组织最终结果
INSERT OVERWRITE TABLE {{ table_name }} PARTITION (pt='${PT_DATE}')
SELECT 
    {{ entity }}_sk,
    {{ business_key }},
    {% for field in fields %}
    {{ field.name }},
    {% endfor %}
    begin_date,
    end_date,
    is_active,
    etl_insert_time,
    etl_update_time
FROM (
    -- 新增或变化后的新记录
    SELECT
        ROW_NUMBER() OVER (ORDER BY {{ business_key }}) + 
            COALESCE(MAX({{ entity }}_sk), 0) AS {{ entity }}_sk,  -- 分配新的SK
        new.{{ business_key }},
        {% for field in fields %}
        new.{{ field.name }},
        {% endfor %}
        '${PT_DATE}' AS begin_date,
        '9999-12-31' AS end_date,
        1 AS is_active,
        CURRENT_TIMESTAMP() AS etl_insert_time,
        CURRENT_TIMESTAMP() AS etl_update_time
    FROM tmp_dim_{{ entity }}_new new
    LEFT ANTI JOIN (
        SELECT {{ business_key }} FROM {{ table_name }} WHERE is_active = 1
    ) old
        ON new.{{ business_key }} = old.{{ business_key }}
    
    UNION ALL
    
    -- 已变化的旧记录（标记为失效）
    SELECT 
        *
    FROM tmp_dim_{{ entity }}_changed
    
    UNION ALL
    
    -- 保留未变化的历史记录
    SELECT
        {{ entity }}_sk,
        {{ business_key }},
        {% for field in fields %}
        {{ field.name }},
        {% endfor %}
        begin_date,
        end_date,
        is_active,
        etl_insert_time,
        etl_update_time
    FROM {{ table_name }}
    WHERE is_active IN (0, 1) AND pt != '${PT_DATE}'
) combined_data
ORDER BY {{ business_key }}, begin_date;

-- 清理临时表
DROP TABLE IF EXISTS tmp_dim_{{ entity }}_new;
DROP TABLE IF EXISTS tmp_dim_{{ entity }}_changed;


{% elif scd_type == 3 %}
-- ========== SCD Type III: 混合型(当前值+前一值) ==========
-- 同时保存当前值和前一个值，用于简单对比分析

MERGE INTO {{ table_name }} t
USING (
    SELECT
        new.{{ business_key }},
        {% for field in fields %}
        new.{{ field.name }} AS current_{{ field.name }},
        old.{{ field.name }} AS prior_{{ field.name }},
        {% endfor %}
        '${PT_DATE}' AS effective_date,
        CURRENT_TIMESTAMP() AS etl_time
    FROM dws_{{ domain }}_{{ entity }}_di new
    LEFT JOIN {{ table_name }} old
        ON new.{{ business_key }} = old.{{ business_key }}
    WHERE new.pt = '${PT_DATE}' AND new.is_valid = 1
) s
ON t.{{ business_key }} = s.{{ business_key }}
WHEN MATCHED THEN
    UPDATE SET
    {% for field in fields %}
    t.{{ field.name }} = s.current_{{ field.name }},
    t.prior_{{ field.name }} = s.prior_{{ field.name }},
    {% endfor %}
    t.effective_date = s.effective_date,
    t.etl_update_time = s.etl_time
WHEN NOT MATCHED THEN
    INSERT (
        {{ entity }}_sk,
        {{ business_key }},
        {% for field in fields %}
        {{ field.name }},
        prior_{{ field.name }},
        {% endfor %}
        effective_date,
        etl_insert_time,
        etl_update_time
    )
    VALUES (
        ROW_NUMBER() OVER (ORDER BY s.{{ business_key }}),
        s.{{ business_key }},
        {% for field in fields %}
        s.current_{{ field.name }},
        NULL,
        {% endfor %}
        s.effective_date,
        s.etl_time,
        s.etl_time
    );

{% endif %}
