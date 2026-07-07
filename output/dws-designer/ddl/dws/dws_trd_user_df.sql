-- DWS表: dws_trd_user_df
-- 说明: 交易域用户日粒度汇总
-- 生成时间: 2026-07-07

CREATE TABLE IF NOT EXISTS dws_trd_user_df (
  user_id BIGINT COMMENT '用户ID',
  gender STRING COMMENT '性别',
  register_channel STRING COMMENT '注册渠道',
  order_cnt BIGINT COMMENT '下单笔数',
  total_amount_sum DECIMAL(18,2) COMMENT '订单总金额(全额)',
  pay_amount_sum DECIMAL(18,2) COMMENT '实付金额',
  discount_amount_sum DECIMAL(18,2) COMMENT '优惠金额',
  payment_cnt BIGINT COMMENT '支付笔数',
  payment_amount_sum DECIMAL(18,2) COMMENT '支付金额',
  refund_cnt BIGINT COMMENT '退款笔数',
  refund_amount_sum DECIMAL(18,2) COMMENT '退款金额'
) COMMENT '交易域用户日粒度汇总'
PARTITIONED BY (dt STRING COMMENT '统计日期')
STORED AS ORC;
