-- ========================================
-- DIM 维度表 ETL SQL 模板
-- ========================================
-- 用于生成 DIM 维度表的加载脚本
-- 支持 SCD Type I 和 Type II 处理


-- ========== SCD Type I: 覆盖更新 ==========
-- 新的维度值直接覆盖旧值，不保留历史
-- 适用于变化频繁且不需要追踪历史的维度

INSERT OVERWRITE TABLE dim_date PARTITION (pt='${PT_DATE}')
SELECT
    ROW_NUMBER() OVER (ORDER BY date_id) AS date_sk,  -- 生成代理键
    
    date_name,
    
    date_code,
    
    CURRENT_TIMESTAMP() AS etl_insert_time,
    CURRENT_TIMESTAMP() AS etl_update_time
FROM dws_default_date_di
WHERE pt = '${PT_DATE}'
    AND is_valid = 1;


