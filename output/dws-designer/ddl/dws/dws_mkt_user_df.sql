-- DWS表: dws_mkt_user_df
-- 说明: 营销域用户日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_mkt_user_df (
  user_id BIGINT COMMENT '用户ID',
  gender STRING COMMENT '性别',
  register_channel STRING COMMENT '注册渠道',
  coupon_use_cnt BIGINT COMMENT '优惠券使用次数'
) COMMENT '营销域用户日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
