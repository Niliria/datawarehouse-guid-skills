-- DWS ETL: dws_trd_sku_df
-- 说明: 交易域商品日粒度汇总
-- 主粒度: 商品SKU ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_trd_sku_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.sku_sk AS sku_id,
  k.sku_name AS sku_name,
  k.category_name AS category_name,
  SUM(f.quantity) AS order_quantity_sum,
  SUM(f.original_amount) AS original_amount_sum,
  SUM(f.split_amount) AS split_amount_sum,
  COUNT(f.refund_id) AS refund_cnt,
  SUM(f.refund_amount) AS refund_amount_sum
FROM dwd_trd_order_detail_df f
LEFT JOIN dim_sku k
  ON f.sku_sk = k.sku_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.sku_sk,
  k.sku_name,
  k.category_name;
