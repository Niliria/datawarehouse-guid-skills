-- DWS表: dws_mkt_coupon_df
-- 说明: 营销域优惠券日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_mkt_coupon_df (
  coupon_id BIGINT COMMENT '优惠券ID',
  coupon_name STRING COMMENT '优惠券名称',
  discount_type TINYINT COMMENT '优惠类型',
  coupon_use_cnt BIGINT COMMENT '优惠券使用次数'
) COMMENT '营销域优惠券日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
