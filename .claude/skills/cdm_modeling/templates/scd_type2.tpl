-- ========================================
-- SCD Type II 拉链表 ETL SQL 模板 (详细版)
-- ========================================
-- 完整的拉链表实现逻辑
-- 用于处理需要追踪完整历史的维度表

-- 说明：
-- 拉链表用两个日期字段(begin_date, end_date)标记数据的有效期
-- is_active = 1 表示当前有效记录, = 0 表示历史记录
-- 当维度属性变化时，旧记录end_date更新，新记录插入

-- ========================================
-- 拉链表全量覆盖方案 (推荐)
-- ========================================
-- 每次ETL都输出完整的维度表，包括历史和当前

INSERT OVERWRITE TABLE {{ table_name }} PARTITION (pt='${PT_DATE}')
SELECT
    {{ entity }}_sk,
    {{ business_key }},
    {% for attr in attributes %}
    {{ attr.name }},
    {% endfor %}
    begin_date,
    end_date,
    is_active,
    etl_insert_time,
    etl_update_time
FROM (
    -- 第1部分：历史记录（已经过期的、未变化的）
    SELECT
        {{ entity }}_sk,
        {{ business_key }},
        {% for attr in attributes %}
        {{ attr.name }},
        {% endfor %}
        begin_date,
        end_date,
        is_active,
        etl_insert_time,
        etl_update_time
    FROM {{ table_name }}
    WHERE is_active = 0  -- 已失效的历史记录，保持不变
       OR (is_active = 1 AND {{ business_key }} NOT IN (
            SELECT {{ business_key }} 
            FROM dws_{{ domain }}_{{ entity }}_di 
            WHERE pt = '${PT_DATE}'
           ))  -- 当前记录如果新数据中不存在，则保持不变
    
    UNION ALL
    
    -- 第2部分：需要关闭的旧记录（属性已变化）
    SELECT
        old.{{ entity }}_sk,
        old.{{ business_key }},
        {% for attr in attributes %}
        old.{{ attr.name }},
        {% endfor %}
        old.begin_date,
        '${PT_DATE}' AS end_date,  -- 标记为：今天失效
        0 AS is_active             -- 标记为：历史记录
    FROM {{ table_name }} old
    INNER JOIN dws_{{ domain }}_{{ entity }}_di new
        ON old.{{ business_key }} = new.{{ business_key }}
    WHERE old.is_active = 1  -- 只处理当前活跃的记录
      AND new.pt = '${PT_DATE}'
      AND (
          -- 至少一个属性发生了变化
          {% for attr in attributes %}
          NVL(old.{{ attr.name }}, '') != NVL(new.{{ attr.name }}, '')
          {% if not loop.last %} OR {% endif %}
          {% endfor %}
      )
    
    UNION ALL
    
    -- 第3部分：新增或已变化的新记录
    SELECT
        ROW_NUMBER() OVER (ORDER BY new.{{ business_key }}) 
            + CAST(MAX({{ entity }}_sk) OVER () AS BIGINT) AS {{ entity }}_sk,
        new.{{ business_key }},
        {% for attr in attributes %}
        new.{{ attr.name }},
        {% endfor %}
        '${PT_DATE}' AS begin_date,    -- 今天生效
        '9999-12-31' AS end_date,      -- 暂无失效日期
        1 AS is_active                 -- 标记为：当前记录
    FROM dws_{{ domain }}_{{ entity }}_di new
    WHERE new.pt = '${PT_DATE}'
      AND (
          -- 新增的记录（不存在旧数据）
          new.{{ business_key }} NOT IN (
              SELECT {{ business_key }} FROM {{ table_name }}
          )
          -- 或已变化的新值（需要替换）
          OR new.{{ business_key }} IN (
              SELECT {{ business_key }}
              FROM {{ table_name }}
              WHERE is_active = 1
          )
      )
) combined_data
ORDER BY {{ business_key }}, begin_date DESC;


-- ========================================
-- 数据质量验证查询
-- ========================================

-- 验证1：检查是否存在时间穿插问题
SELECT
    '时间穿插检查' AS check_name,
    COUNT(*) AS error_count
FROM {{ table_name }} t1
WHERE EXISTS (
    SELECT 1
    FROM {{ table_name }} t2
    WHERE t1.{{ business_key }} = t2.{{ business_key }}
      AND t1.begin_date < t2.begin_date
      AND t1.end_date > t2.begin_date
);

-- 验证2：检查是否存在未关闭的旧记录
SELECT
    '旧记录未关闭检查' AS check_name,
    COUNT(*) AS error_count
FROM {{ table_name }} t1
WHERE is_active = 1
  AND end_date != '9999-12-31'
GROUP BY pt;

-- 验证3：检查当前记录数
SELECT
    '当前记录统计' AS metric_name,
    COUNT(DISTINCT {{ business_key }}) AS current_record_count,
    COUNT(*) AS total_rows_with_history,
    pt
FROM {{ table_name }}
WHERE is_active = 1
GROUP BY pt;

-- 验证4：变化率分析
SELECT
    '变化率分析' AS analysis,
    COUNT(DISTINCT {{ business_key }}) AS changed_records,
    COUNT(*) AS total_historical_rows,
    ROUND(100.0 * COUNT(*) / COUNT(DISTINCT {{ business_key }}), 2) AS avg_versions_per_record,
    pt
FROM {{ table_name }}
WHERE is_active = 0
GROUP BY pt;


-- ========================================
-- 拉链表增量方案 (备选)
-- ========================================
-- 仅处理当天变化，性能更优但需要维护增量逻辑

-- DROP TABLE IF EXISTS tmp_scd2_updates;
-- CREATE TABLE tmp_scd2_updates AS
-- -- 1. 已存在且未变化的记录 → 保持不变
-- SELECT 
--     {{ entity }}_sk,
--     {{ business_key }},
--     {% for attr in attributes %} {{ attr.name }}, {% endfor %}
--     begin_date,
--     end_date,
--     is_active,
--     etl_insert_time,
--     etl_update_time
-- FROM {{ table_name }}
-- 
-- UNION ALL
-- 
-- -- 2. 已存在且发生变化的旧记录 → 更新end_date和is_active
-- SELECT 
--     old.{{ entity }}_sk,
--     old.{{ business_key }},
--     {% for attr in attributes %} old.{{ attr.name }}, {% endfor %}
--     old.begin_date,
--     '${PT_DATE}' AS end_date,
--     0 AS is_active,
--     old.etl_insert_time,
--     CURRENT_TIMESTAMP() AS etl_update_time
-- FROM {{ table_name }} old
-- WHERE old.is_active = 1
--   AND EXISTS(
--       SELECT 1 FROM dws_{{ domain }}_{{ entity }}_di new
--       WHERE old.{{ business_key }} = new.{{ business_key }}
--         AND new.pt = '${PT_DATE}'
--         AND ({{ changed_condition }})
--   )
-- 
-- UNION ALL
-- 
-- -- 3. 新增或变化的新记录 → 插入新行
-- SELECT 
--     ...,
--     '${PT_DATE}' AS begin_date,
--     '9999-12-31' AS end_date,
--     1 AS is_active
-- FROM dws_...
-- 
-- ORDER BY {{ business_key }}, begin_date;
