# CDM Model Design

## DIM Tables

- `dim_coupon`: entity `coupon`, SCD Type 1, business key `coupon_id`
- `dim_shop`: entity `shop`, SCD Type 1, business key `shop_id`
- `dim_sku`: entity `sku`, SCD Type 2, business key `sku_id`
- `dim_user`: entity `user`, SCD Type 2, business key `user_id`

## DWD Tables

- `dwd_inv_inventory_snapshot_df`: process `inventory_snapshot`, grain `一行一个门店一个SKU的库存快照`, fact type `periodic_snapshot`
- `dwd_mkt_coupon_usage_df`: process `coupon_usage`, grain `一行一张用户领取的优惠券`, fact type `factless`
- `dwd_trd_order_detail_df`: process `order_detail`, grain `一行一笔订单中的一个商品明细行`, fact type `transaction`
- `dwd_trd_payment_df`: process `payment`, grain `一行一笔支付交易`, fact type `transaction`
- `dwd_trd_place_order_df`: process `place_order`, grain `一行一笔订单`, fact type `transaction`
- `dwd_trd_refund_df`: process `refund`, grain `一行一笔退款申请`, fact type `transaction`
