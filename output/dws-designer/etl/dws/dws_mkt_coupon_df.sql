-- DWS ETL: dws_mkt_coupon_df
-- 说明: 营销域优惠券日粒度汇总
-- 主粒度: 优惠券ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_mkt_coupon_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.coupon_sk AS coupon_id,
  c.coupon_name AS coupon_name,
  c.discount_type AS discount_type,
  COUNT(f.id) AS coupon_use_cnt
FROM dwd_mkt_coupon_usage_df f
LEFT JOIN dim_coupon c
  ON f.coupon_sk = c.coupon_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.coupon_sk,
  c.coupon_name,
  c.discount_type;
