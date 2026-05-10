-- ========================================
-- DIM 店铺维度表 (SCD Type I)
-- 来源: ods_shop_master_df
-- 业务键: shop_id
-- ========================================

CREATE TABLE IF NOT EXISTS dim_shop (
    -- 维度键
    shop_sk BIGINT COMMENT '店铺代理键(维度主键)',
    shop_id BIGINT COMMENT '店铺业务键(来自ODS)',

    -- 维度属性
    shop_name STRING COMMENT '店铺名称',
    region_id BIGINT COMMENT '地区ID',
    region_name STRING COMMENT '地区名称',
    city STRING COMMENT '城市',

    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间'
)
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.stripe.size'='67108864'
);