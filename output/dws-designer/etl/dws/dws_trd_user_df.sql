-- DWS ETL: dws_trd_user_df
-- 说明: 交易域用户日粒度汇总
-- 主粒度: 用户ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_trd_user_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.user_sk AS user_id,
  u.gender AS gender,
  u.register_channel AS register_channel,
  COUNT(f.order_id) AS order_cnt,
  SUM(f.total_amount) AS total_amount_sum,
  SUM(f.pay_amount) AS pay_amount_sum,
  SUM(f.discount_amount) AS discount_amount_sum,
  COUNT(f.pay_id) AS payment_cnt,
  SUM(f.pay_amount) AS payment_amount_sum,
  COUNT(f.refund_id) AS refund_cnt,
  SUM(f.refund_amount) AS refund_amount_sum
FROM dwd_trd_place_order_df f
LEFT JOIN dim_user u
  ON f.user_sk = u.user_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.user_sk,
  u.gender,
  u.register_channel;
