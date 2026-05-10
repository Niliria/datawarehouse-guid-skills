-- ========================================
-- DIM 维度表 DDL 模板
-- ========================================
-- 用于生成 DIM 维度表的建表语句
-- 支持 SCD Type I 和 Type II


-- ========== SCD Type I: 覆盖更新 ==========
CREATE TABLE IF NOT EXISTS dim_date (
    -- 维度键
    date_sk BIGINT COMMENT 'date代理键(PK)',
    date_id BIGINT COMMENT 'date业务键(来自ODS)',
    
    -- 维度属性
    
    date_name STRING COMMENT '日期名称',
    
    date_code STRING COMMENT '日期编码',
    
    
    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间'
)
COMMENT '维度表: date'
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

