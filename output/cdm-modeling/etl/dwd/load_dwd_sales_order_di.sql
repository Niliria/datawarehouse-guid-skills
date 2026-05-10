-- ========================================
-- DWD 销售订单事实表 ETL 加载脚本
-- 来源: ods_sales_order_di
-- 星形结构: JOIN 维度表获取代理键
-- ========================================

-- 参数: ${PT_DATE} - 分区日期

INSERT OVERWRITE TABLE dwd_sales_order_di PARTITION (pt='${PT_DATE}')
SELECT
    -- 事实键
    ods.order_id,
    ROW_NUMBER() OVER (ORDER BY ods.order_id) AS order_sk,  -- 代理键生成

    -- 维度外键 (JOIN 维度表获取 SK)
    dim_shop.shop_sk,
    dim_date.date_sk,
    dim_product.product_sk,
    dim_customer.customer_sk,

    -- 度量值
    ods.order_amount,
    ods.discount_amount,
    1 AS quantity,  -- 订单计数

    -- 业务标志
    ods.order_status,
    1 AS is_valid,  -- 默认有效

    -- 审计字段
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time,
    'sales_system' AS source_system
FROM ods_sales_order_di ods

-- JOIN 店铺维度 (获取 shop_sk)
LEFT JOIN dim_shop dim_shop
    ON ods.shop_id = dim_shop.shop_id
    AND dim_shop.is_active = 1  -- 只关联当前活跃记录
    AND dim_shop.pt = '${PT_DATE}'

-- JOIN 日期维度 (获取 date_sk)
LEFT JOIN dim_date dim_date
    ON ods.order_date = dim_date.calendar_date
    AND dim_date.pt = '${PT_DATE}'

-- JOIN 商品维度 (获取 product_sk) - 需要从订单明细获取
-- 注意: 当前ODS表缺少 product_id，实际场景需要订单明细表
LEFT JOIN dim_product dim_product
    ON dim_product.product_id = -1  -- 占位，实际需从订单明细获取
    AND dim_product.is_active = 1

-- JOIN 客户维度 (获取 customer_sk)
LEFT JOIN dim_customer dim_customer
    ON ods.customer_id = dim_customer.customer_id
    AND dim_customer.is_active = 1
    AND dim_customer.pt = '${PT_DATE}'

WHERE ods.pt = '${PT_DATE}';

-- 质量检查: 外键缺失率
-- 验证维度JOIN成功率应 >= 99%
SELECT
    'dwd_sales_order_di' AS table_name,
    '${PT_DATE}' AS pt,
    COUNT(*) AS total_rows,
    SUM(CASE WHEN shop_sk IS NULL THEN 1 ELSE 0 END) AS shop_sk_missing,
    SUM(CASE WHEN customer_sk IS NULL THEN 1 ELSE 0 END) AS customer_sk_missing,
    ROUND(SUM(CASE WHEN shop_sk IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS shop_missing_rate,
    ROUND(SUM(CASE WHEN customer_sk IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS customer_missing_rate
FROM dwd_sales_order_di
WHERE pt = '${PT_DATE}';