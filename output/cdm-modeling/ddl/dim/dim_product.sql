-- ========================================
-- DIM 商品维度表 (SCD Type II 拉链表)
-- 来源: ods_product_master_df
-- 业务键: product_id
-- ========================================

CREATE TABLE IF NOT EXISTS dim_product (
    -- 维度键
    product_sk BIGINT COMMENT '商品代理键(维度主键)',
    product_id BIGINT COMMENT '商品业务键(来自ODS)',

    -- 维度属性
    product_name STRING COMMENT '商品名称',
    category_id BIGINT COMMENT '分类ID',
    category_name STRING COMMENT '分类名称',
    price DECIMAL(18,2) COMMENT '商品价格',

    -- SCD Type II 字段
    begin_date STRING COMMENT '维度值生效日期(开始日期,YYYY-MM-DD)',
    end_date STRING COMMENT '维度值失效日期(结束日期,当前记录为9999-12-31)',
    is_active INT COMMENT '是否当前活跃记录(1=当前,0=历史)',

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