-- DWS表: dws_trd_sku_df
-- 说明: 交易域商品日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_trd_sku_df (
  sku_id BIGINT COMMENT '商品SKU ID',
  sku_name STRING COMMENT '商品名称',
  category_name STRING COMMENT '品类名称',
  order_quantity_sum BIGINT COMMENT '销售数量',
  original_amount_sum DECIMAL(18,2) COMMENT '原价金额(全额)',
  split_amount_sum DECIMAL(18,2) COMMENT '分摊金额(全额)',
  refund_cnt BIGINT COMMENT '退款笔数',
  refund_amount_sum DECIMAL(18,2) COMMENT '退款金额'
) COMMENT '交易域商品日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
