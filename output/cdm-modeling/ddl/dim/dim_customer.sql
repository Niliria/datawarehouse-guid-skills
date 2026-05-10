-- ========================================
-- DIM 客户维度表 (SCD Type II 拉链表)
-- 来源: ods_customer_master_df
-- 业务键: customer_id
-- ========================================

CREATE TABLE IF NOT EXISTS dim_customer (
    -- 维度键
    customer_sk BIGINT COMMENT '客户代理键(维度主键)',
    customer_id BIGINT COMMENT '客户业务键(来自ODS)',

    -- 维度属性
    customer_name STRING COMMENT '客户名称',
    customer_level STRING COMMENT '客户等级',
    register_date STRING COMMENT '注册日期',

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