-- DWS ETL: dws_mkt_user_df
-- 说明: 营销域用户日粒度汇总
-- 主粒度: 用户ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_mkt_user_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.user_sk AS user_id,
  u.gender AS gender,
  u.register_channel AS register_channel,
  COUNT(f.id) AS coupon_use_cnt
FROM dwd_mkt_coupon_usage_df f
LEFT JOIN dim_user u
  ON f.user_sk = u.user_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.user_sk,
  u.gender,
  u.register_channel;
