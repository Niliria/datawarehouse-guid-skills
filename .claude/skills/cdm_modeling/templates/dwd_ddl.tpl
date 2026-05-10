-- ========================================
-- DWD 事实表 DDL 模板
-- ========================================
-- 用于生成 DWD 事实表的建表语句
-- 星形结构：中心是事实表，外围是维度表

CREATE TABLE IF NOT EXISTS {{ table_name }} (
    -- 事实键
    {{ business_key }} STRING COMMENT '{{ entity }}业务键(来自上游总线矩阵粒度)',
    {{ entity }}_sk BIGINT COMMENT '{{ entity }}代理键(事实主键)',

    -- 维度外键（包含所有维度：业务维度+日期维度）
    {% for dim in dimensions %}
    {{ dim.entity }}_sk BIGINT COMMENT '→ dim_{{ dim.entity }}(外键)',
    {% endfor %}

    -- 度量值(可加总)
    {% for measure in measures %}
    {{ measure.name }} {{ measure.type }} COMMENT '{{ measure.description }}(聚合函数:{{ measure.aggregation }})',
    {% endfor %}

    -- 业务标志
    is_valid INT COMMENT '是否有效记录(1=有效,0=无效)',

    -- 审计字段
    etl_insert_time TIMESTAMP COMMENT 'ETL插入时间',
    etl_update_time TIMESTAMP COMMENT 'ETL更新时间',
    source_system STRING COMMENT '来源系统'
)
COMMENT '{{ table_comment }}'
PARTITIONED BY (pt STRING COMMENT '分区日期(YYYY-MM-DD)')
STORED AS ORC
TBLPROPERTIES (
    'orc.compress'='SNAPPY',
    'orc.stripe.size'='67108864'
);
