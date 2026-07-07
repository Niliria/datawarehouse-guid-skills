-- DWS ETL: dws_trd_shop_df
-- 说明: 交易域门店日粒度汇总
-- 主粒度: 门店ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_trd_shop_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.shop_sk AS shop_id,
  s.shop_name AS shop_name,
  s.city_name AS city_name,
  COUNT(f.order_id) AS order_cnt,
  SUM(f.total_amount) AS total_amount_sum,
  SUM(f.pay_amount) AS pay_amount_sum,
  SUM(f.discount_amount) AS discount_amount_sum
FROM dwd_trd_place_order_df f
LEFT JOIN dim_shop s
  ON f.shop_sk = s.shop_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.shop_sk,
  s.shop_name,
  s.city_name;
