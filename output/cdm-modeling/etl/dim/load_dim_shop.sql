-- ========================================
-- DIM 店铺维度 ETL 加载脚本 (SCD Type I 全量覆盖)
-- 来源: ods_shop_master_df
-- ========================================

-- 参数: ${PT_DATE} - 分区日期

-- SCD Type I: 直接覆盖更新
INSERT OVERWRITE TABLE dim_shop PARTITION (pt='${PT_DATE}')
SELECT
    ROW_NUMBER() OVER (ORDER BY shop_id) AS shop_sk,  -- 代理键生成
    shop_id,
    shop_name,
    region_id,
    region_name,
    city,
    CURRENT_TIMESTAMP AS etl_insert_time,
    CURRENT_TIMESTAMP AS etl_update_time
FROM ods_shop_master_df
WHERE pt = '${PT_DATE}';