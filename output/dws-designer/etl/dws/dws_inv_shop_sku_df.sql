-- DWS ETL: dws_inv_shop_sku_df
-- 说明: 库存域门店商品日粒度汇总
-- 主粒度: 门店ID
-- 生成时间: 2026-07-07

INSERT OVERWRITE TABLE dws_inv_shop_sku_df PARTITION(dt = '${bizdate}')
SELECT
  '${bizdate}' AS dt,
  f.shop_sk AS shop_id,
  f.sku_sk AS sku_id,
  s.shop_name AS shop_name,
  k.sku_name AS sku_name,
  AVG(f.stock_num) AS stock_num_avg,
  MAX(f.stock_num) AS stock_num_max,
  MIN(f.stock_num) AS stock_num_min
FROM dwd_inv_inventory_snapshot_df f
LEFT JOIN dim_shop s
  ON f.shop_sk = s.shop_id
LEFT JOIN dim_sku k
  ON f.sku_sk = k.sku_id
WHERE f.dt = '${bizdate}'
  AND f.is_valid = 1
GROUP BY
  f.shop_sk,
  f.sku_sk,
  s.shop_name,
  k.sku_name;
