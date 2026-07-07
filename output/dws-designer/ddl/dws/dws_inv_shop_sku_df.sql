-- DWS表: dws_inv_shop_sku_df
-- 说明: 库存域门店商品日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_inv_shop_sku_df (
  shop_id BIGINT COMMENT '门店ID',
  sku_id BIGINT COMMENT '商品SKU ID',
  shop_name STRING COMMENT '门店名称',
  sku_name STRING COMMENT '商品名称',
  stock_num_avg DECIMAL(18,2) COMMENT '平均库存数量',
  stock_num_max BIGINT COMMENT '最大库存数量',
  stock_num_min BIGINT COMMENT '最小库存数量'
) COMMENT '库存域门店商品日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
