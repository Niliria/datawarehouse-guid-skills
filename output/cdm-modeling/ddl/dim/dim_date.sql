-- ========================================
-- DIM 日期维度表 (标准维度)
-- 算法生成，无ODS来源
-- ========================================

CREATE TABLE IF NOT EXISTS dim_date (
    -- 维度键
    date_sk BIGINT COMMENT '日期代理键(维度主键)',
    calendar_date STRING COMMENT '日期(YYYY-MM-DD)',

    -- 日期属性
    year INT COMMENT '年份',
    quarter INT COMMENT '季度(1-4)',
    quarter_name STRING COMMENT '季度名称(Q1/Q2/Q3/Q4)',
    month INT COMMENT '月份(1-12)',
    month_name STRING COMMENT '月份名称',
    week_of_year INT COMMENT '年内周数',
    day_of_week INT COMMENT '周内日数(1-7)',
    day_name STRING COMMENT '星期名称',
    is_weekend INT COMMENT '是否周末(1=是,0=否)',
    is_holiday INT COMMENT '是否节假日(1=是,0=否)',

    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间'
)
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.stripe.size'='67108864'
);