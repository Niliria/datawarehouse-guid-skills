-- ========================================
-- DWD 销售订单事实表 (事务事实表)
-- 来源: ods_sales_order_di
-- 粒度: 订单
-- 维度: 店铺+日期+商品+客户
-- ========================================

CREATE TABLE IF NOT EXISTS dwd_sales_order_di (
    -- 事实键
    order_id BIGINT COMMENT '订单业务键(来自ODS)',
    order_sk BIGINT COMMENT '订单代理键(事实主键)',

    -- 维度外键
    shop_sk BIGINT COMMENT '→ dim_shop(店铺维度外键)',
    date_sk BIGINT COMMENT '→ dim_date(日期维度外键)',
    product_sk BIGINT COMMENT '→ dim_product(商品维度外键)',
    customer_sk BIGINT COMMENT '→ dim_customer(客户维度外键)',

    -- 度量值
    order_amount DECIMAL(18,2) COMMENT '订单金额(聚合:SUM)',
    discount_amount DECIMAL(18,2) COMMENT '折扣金额(聚合:SUM)',
    quantity INT COMMENT '数量(聚合:COUNT)',

    -- 业务标志
    order_status STRING COMMENT '订单状态',
    is_valid INT COMMENT '是否有效记录(1=有效,0=无效)',

    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间',
    source_system STRING COMMENT '来源系统'
)
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.stripe.size'='67108864'
);