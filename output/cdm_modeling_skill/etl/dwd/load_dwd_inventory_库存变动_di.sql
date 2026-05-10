-- ========================================
-- DWD 事实表 ETL SQL 模板
-- ========================================
-- 用于生成 DWD 事实表的加载脚本
-- 核心逻辑：从DWS + DIM 通过JOIN生成事实表

-- 步骤1：从DWS获取基础事实数据并JOIN维度表
INSERT OVERWRITE TABLE dwd_inventory_库存变动_di PARTITION (pt='${PT_DATE}')
SELECT
    source.库存变动_id,
    ROW_NUMBER() OVER (ORDER BY source.库存变动_id) AS 库存变动_sk,

    -- 维度外键 (JOIN维度表获取SK)
    
    COALESCE(dim_shop.shop_sk, -1) AS shop_sk,
    
    COALESCE(dim_date.date_sk, -1) AS date_sk,
    
    COALESCE(dim_product.product_sk, -1) AS product_sk,
    

    -- 度量值 (从DWS直接取)
    
    source.quantity,
    
    source.amount
    

    -- 业务标志
    CASE
        WHEN  dim_shop.shop_sk IS NOT NULL
         AND   dim_date.date_sk IS NOT NULL
         AND   dim_product.product_sk IS NOT NULL
         
        THEN 1
        ELSE 0
    END AS is_valid,

    -- 审计字段
    CURRENT_TIMESTAMP() AS etl_insert_time,
    CURRENT_TIMESTAMP() AS etl_update_time,
    'dws_inventory_库存变动' AS source_system

FROM dws_inventory_库存变动_di source


LEFT JOIN dim_shop
    ON source.shop_id = dim_shop.shop_id
    AND dim_shop.is_active = 1
    AND dim_shop.pt = '${PT_DATE}'

LEFT JOIN dim_date
    ON source.date_id = dim_date.date_id
    AND dim_date.is_active = 1
    AND dim_date.pt = '${PT_DATE}'

LEFT JOIN dim_product
    ON source.product_id = dim_product.product_id
    AND dim_product.is_active = 1
    AND dim_product.pt = '${PT_DATE}'


WHERE source.pt = '${PT_DATE}';

-- ========================================
-- 优化后的数据质量检查 (简化版)
-- ========================================
SELECT
    'dwd_inventory_库存变动_di' AS table_name,
    '${PT_DATE}' AS pt,
    COUNT(*) AS total_records,
    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) AS valid_records,
    
    MIN(quantity) AS quantity_min,
    MAX(quantity) AS quantity_max,
    
    MIN(amount) AS amount_min,
    MAX(amount) AS amount_max,
    
    COUNT(DISTINCT shop_sk) AS shop_unique_count

FROM dwd_inventory_库存变动_di
WHERE pt = '${PT_DATE}'
GROUP BY pt;