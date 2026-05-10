-- ========================================
-- DIM 商品维度 ETL 加载脚本 (SCD Type II 拉链表)
-- 来源: ods_product_master_df
-- ========================================

-- 参数: ${PT_DATE} - 分区日期

-- Step 1: 关闭旧记录 (SCD Type II 拉链逻辑)
UPDATE dim_product
SET
    end_date = '${PT_DATE}',
    is_active = 0
WHERE
    is_active = 1
    AND product_id IN (
        SELECT DISTINCT product_id
        FROM ods_product_master_df
        WHERE pt = '${PT_DATE}'
        AND EXISTS (
            SELECT 1 FROM dim_product p2
            WHERE p2.product_id = ods_product_master_df.product_id
            AND p2.is_active = 1
            AND (p2.product_name != ods_product_master_df.product_name
                 OR p2.category_id != ods_product_master_df.category_id
                 OR p2.price != ods_product_master_df.price)
        )
    );

-- Step 2: 插入新版本记录
INSERT INTO dim_product
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) + 1000000 AS product_sk,  -- 代理键生成
    product_id,
    product_name,
    category_id,
    category_name,
    price,
    '${PT_DATE}' AS begin_date,  -- 生效日期
    '9999-12-31' AS end_date,    -- 失效日期(永久)
    1 AS is_active,              -- 当前活跃
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time,
    '${PT_DATE}' AS pt
FROM ods_product_master_df
WHERE pt = '${PT_DATE}';

-- Step 3: 插入全新商品记录
INSERT INTO dim_product
SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_sk,
    product_id,
    product_name,
    category_id,
    category_name,
    price,
    '${PT_DATE}' AS begin_date,
    '9999-12-31' AS end_date,
    1 AS is_active,
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time,
    '${PT_DATE}' AS pt
FROM ods_product_master_df
WHERE pt = '${PT_DATE}'
AND NOT EXISTS (
    SELECT 1 FROM dim_product
    WHERE dim_product.product_id = ods_product_master_df.product_id
);