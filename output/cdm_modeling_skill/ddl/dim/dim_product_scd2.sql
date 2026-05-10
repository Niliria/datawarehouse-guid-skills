-- ========================================
-- DIM 维度表 DDL 模板
-- ========================================
-- 用于生成 DIM 维度表的建表语句
-- 支持 SCD Type I 和 Type II


-- ========== SCD Type II: 拉链表(完整历史) ==========
CREATE TABLE IF NOT EXISTS dim_product (
    -- 维度键
    product_sk BIGINT COMMENT 'product代理键(PK)',
    product_id BIGINT COMMENT 'product业务键(来自ODS)',
    
    -- 维度属性
    
    product_name STRING COMMENT '商品名称',
    
    product_code STRING COMMENT '商品编码',
    
    
    -- SCD II 字段
    begin_date STRING COMMENT '维度值生效日期(开始日期,YYYY-MM-DD)',
    end_date STRING COMMENT '维度值失效日期(结束日期,当前记录为9999-12-31)',
    is_active INT COMMENT '是否当前活跃记录(1=当前,0=历史)',
    
    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间'
)
COMMENT '维度表: product'
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

