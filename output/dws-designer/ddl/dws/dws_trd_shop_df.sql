-- DWS表: dws_trd_shop_df
-- 说明: 交易域门店日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_trd_shop_df (
  shop_id BIGINT COMMENT '门店ID',
  shop_name STRING COMMENT '门店名称',
  city_name STRING COMMENT '城市名称',
  order_cnt BIGINT COMMENT '下单笔数',
  total_amount_sum DECIMAL(18,2) COMMENT '订单总金额(全额)',
  pay_amount_sum DECIMAL(18,2) COMMENT '实付金额',
  discount_amount_sum DECIMAL(18,2) COMMENT '优惠金额'
) COMMENT '交易域门店日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
