-- ========================================
-- DWD 事实表 ETL SQL 模板
-- ========================================
-- 用于生成 DWD 事实表的加载脚本
-- 核心逻辑：从DWS + DIM 通过JOIN生成事实表

-- 步骤1：从DWS获取基础事实数据并JOIN维度表
INSERT OVERWRITE TABLE {{ table_name }} PARTITION (pt='${PT_DATE}')
SELECT
    source.{{ entity }}_id,
    ROW_NUMBER() OVER (ORDER BY source.{{ entity }}_id) AS {{ entity }}_sk,

    -- 维度外键 (JOIN维度表获取SK)
    {% for dim in dimensions %}
    COALESCE(dim_{{ dim.entity }}.{{ dim.entity }}_sk, -1) AS {{ dim.entity }}_sk,
    {% endfor %}

    -- 度量值 (从DWS直接取)
    {% for measure in measures %}
    source.{{ measure.name }}{% if not loop.last %},{% endif %}
    {% endfor %}

    -- 业务标志
    CASE
        WHEN {% for dim in dimensions %} dim_{{ dim.entity }}.{{ dim.entity }}_sk IS NOT NULL
        {% if not loop.last %} AND {% endif %} {% endfor %}
        THEN 1
        ELSE 0
    END AS is_valid,

    -- 审计字段
    CURRENT_TIMESTAMP() AS etl_insert_time,
    CURRENT_TIMESTAMP() AS etl_update_time,
    'dws_{{ domain }}_{{ entity }}' AS source_system

FROM dws_{{ domain }}_{{ entity }}_di source

{% for dim in dimensions %}
LEFT JOIN dim_{{ dim.entity }}
    ON source.{{ dim.entity }}_id = dim_{{ dim.entity }}.{{ dim.entity }}_id
    AND dim_{{ dim.entity }}.is_active = 1
    AND dim_{{ dim.entity }}.pt = '${PT_DATE}'
{% endfor %}

WHERE source.pt = '${PT_DATE}';

-- ========================================
-- 优化后的数据质量检查 (简化版)
-- ========================================
SELECT
    '{{ table_name }}' AS table_name,
    '${PT_DATE}' AS pt,
    COUNT(*) AS total_records,
    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) AS valid_records,
    {% for measure in measures %}
    MIN({{ measure.name }}) AS {{ measure.name }}_min,
    MAX({{ measure.name }}) AS {{ measure.name }}_max,
    {% endfor %}
    COUNT(DISTINCT {{ dimensions[0].entity }}_sk) AS {{ dimensions[0].entity }}_unique_count

FROM {{ table_name }}
WHERE pt = '${PT_DATE}'
GROUP BY pt;
