-- ========================================
-- DIM 客户维度 ETL 加载脚本 (SCD Type II 拉链表)
-- 来源: ods_customer_master_df
-- ========================================

-- 参数: ${PT_DATE} - 分区日期

-- Step 1: 关闭旧记录 (SCD Type II 拉链逻辑)
UPDATE dim_customer
SET
    end_date = '${PT_DATE}',
    is_active = 0
WHERE
    is_active = 1
    AND customer_id IN (
        SELECT DISTINCT customer_id
        FROM ods_customer_master_df
        WHERE pt = '${PT_DATE}'
        AND EXISTS (
            SELECT 1 FROM dim_customer c2
            WHERE c2.customer_id = ods_customer_master_df.customer_id
            AND c2.is_active = 1
            AND (c2.customer_name != ods_customer_master_df.customer_name
                 OR c2.customer_level != ods_customer_master_df.customer_level)
        )
    );

-- Step 2: 插入新版本记录
INSERT INTO dim_customer
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) + 1000000 AS customer_sk,  -- 代理键生成
    customer_id,
    customer_name,
    customer_level,
    register_date,
    '${PT_DATE}' AS begin_date,  -- 生效日期
    '9999-12-31' AS end_date,    -- 失效日期(永久)
    1 AS is_active,              -- 当前活跃
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time,
    '${PT_DATE}' AS pt
FROM ods_customer_master_df
WHERE pt = '${PT_DATE}';

-- Step 3: 插入全新客户记录
INSERT INTO dim_customer
SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_sk,
    customer_id,
    customer_name,
    customer_level,
    register_date,
    '${PT_DATE}' AS begin_date,
    '9999-12-31' AS end_date,
    1 AS is_active,
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time,
    '${PT_DATE}' AS pt
FROM ods_customer_master_df
WHERE pt = '${PT_DATE}'
AND NOT EXISTS (
    SELECT 1 FROM dim_customer
    WHERE dim_customer.customer_id = ods_customer_master_df.customer_id
);