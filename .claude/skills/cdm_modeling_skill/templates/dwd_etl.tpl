-- ========================================
-- DWD 事实表 ETL SQL 模板
-- ========================================
-- 来源：上游总线矩阵文档提供的粒度、维度、度量和源表映射

INSERT OVERWRITE TABLE {{ table_name }} PARTITION (pt='${PT_DATE}')
SELECT
    CAST(source.{{ business_key }} AS STRING) AS {{ business_key }},
    ROW_NUMBER() OVER (ORDER BY source.{{ business_key }}) AS {{ entity }}_sk,

{% for dim in dimensions %}
    COALESCE(dim_{{ dim.entity }}.{{ dim.entity }}_sk, -1) AS {{ dim.entity }}_sk,
{% endfor %}

{% for measure in measures %}
    source.{{ measure.source_field | default(measure.name) }} AS {{ measure.name }},
{% endfor %}

    CASE
        WHEN {% for dim in dimensions %}dim_{{ dim.entity }}.{{ dim.entity }}_sk IS NOT NULL{% if not loop.last %} AND {% endif %}{% endfor %}
        THEN 1
        ELSE 0
    END AS is_valid,
    CURRENT_TIMESTAMP() AS etl_insert_time,
    CURRENT_TIMESTAMP() AS etl_update_time,
    '{{ source_table }}' AS source_system
FROM {{ source_table }} source
{% for dim in dimensions %}
LEFT JOIN dim_{{ dim.entity }}
    ON source.{{ dim.business_key }} = dim_{{ dim.entity }}.{{ dim.business_key }}
   AND dim_{{ dim.entity }}.pt = '${PT_DATE}'
{% endfor %}
WHERE source.pt = '${PT_DATE}';

-- 数据质量检查
SELECT
    '{{ table_name }}' AS table_name,
    '${PT_DATE}' AS pt,
    COUNT(*) AS total_records,
    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) AS valid_records{% if measures %},{% endif %}
{% for measure in measures %}
    MIN({{ measure.name }}) AS {{ measure.name }}_min,
    MAX({{ measure.name }}) AS {{ measure.name }}_max{% if not loop.last %},{% endif %}
{% endfor %}
FROM {{ table_name }}
WHERE pt = '${PT_DATE}';
