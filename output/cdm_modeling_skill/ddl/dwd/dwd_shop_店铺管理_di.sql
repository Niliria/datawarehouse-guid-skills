-- ========================================
-- DWD 事实表 DDL 模板
-- ========================================
-- 用于生成 DWD 事实表的建表语句
-- 星形结构：中心是事实表，外围是维度表

CREATE TABLE IF NOT EXISTS dwd_shop_店铺管理_di (
    -- 事实键
    店铺管理_id STRING COMMENT '店铺管理业务键(来自ODS)',
    店铺管理_sk BIGINT COMMENT '店铺管理代理键(事实主键)',

    -- 维度外键（包含所有维度：业务维度+日期维度）
    
    shop_sk BIGINT COMMENT '→ dim_shop(外键)',
    
    date_sk BIGINT COMMENT '→ dim_date(外键)',
    

    -- 度量值(可加总)
    
    quantity BIGINT COMMENT '数量(聚合函数:SUM)',
    
    amount DECIMAL(18,2) COMMENT '金额(聚合函数:SUM)',
    

    -- 业务标志
    is_valid INT COMMENT '是否有效记录(1=有效,0=无效)',

    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间',
    source_system STRING COMMENT '来源系统'
)
COMMENT '事实表: shop-店铺管理'
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.stripe.size'='67108864'
);