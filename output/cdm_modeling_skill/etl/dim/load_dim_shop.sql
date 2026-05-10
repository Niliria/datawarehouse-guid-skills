-- ========================================
-- DIM 维度表 ETL SQL 模板
-- ========================================
-- 用于生成 DIM 维度表的加载脚本
-- 支持 SCD Type I 和 Type II 处理


-- ========== SCD Type II: 拉链表(完整历史) ==========
-- 维度值变化时生成新记录，旧记录标记为失效
-- 记录开始日期和结束日期，支持时间维度分析

-- 步骤1：临时表 - 承载最新的DWS数据
DROP TABLE IF EXISTS tmp_dim_shop_new;
CREATE TABLE tmp_dim_shop_new AS
SELECT
    shop_id,
    
    shop_name,
    
    shop_code,
    
    CURRENT_TIMESTAMP() AS etl_time
FROM dws_default_shop_di
WHERE pt = '${PT_DATE}'
    AND is_valid = 1;

-- 步骤2：识别变化的记录
-- 旧记录存在但新值不同 = 发生了变化
DROP TABLE IF EXISTS tmp_dim_shop_changed;
CREATE TABLE tmp_dim_shop_changed AS
SELECT
    old.shop_sk,
    old.shop_id,
    
    old.shop_name,
    
    old.shop_code,
    
    '${PT_DATE}' AS end_date,    -- 旧记录失效时间
    0 AS is_active
FROM dim_shop old
INNER JOIN tmp_dim_shop_new new
    ON old.shop_id = new.shop_id
    AND old.is_active = 1
WHERE
    -- 至少一个属性发生变化
    
    NVL(old.shop_name, '') != NVL(new.shop_name, '')
     OR 
    
    NVL(old.shop_code, '') != NVL(new.shop_code, '')
    
    ;

-- 步骤3：组织最终结果
INSERT OVERWRITE TABLE dim_shop PARTITION (pt='${PT_DATE}')
SELECT 
    shop_sk,
    shop_id,
    
    shop_name,
    
    shop_code,
    
    begin_date,
    end_date,
    is_active,
    etl_insert_time,
    etl_update_time
FROM (
    -- 新增或变化后的新记录
    SELECT
        ROW_NUMBER() OVER (ORDER BY shop_id) + 
            COALESCE(MAX(shop_sk), 0) AS shop_sk,  -- 分配新的SK
        new.shop_id,
        
        new.shop_name,
        
        new.shop_code,
        
        '${PT_DATE}' AS begin_date,
        '9999-12-31' AS end_date,
        1 AS is_active,
        CURRENT_TIMESTAMP() AS etl_insert_time,
        CURRENT_TIMESTAMP() AS etl_update_time
    FROM tmp_dim_shop_new new
    LEFT ANTI JOIN (
        SELECT shop_id FROM dim_shop WHERE is_active = 1
    ) old
        ON new.shop_id = old.shop_id
    
    UNION ALL
    
    -- 已变化的旧记录（标记为失效）
    SELECT 
        *
    FROM tmp_dim_shop_changed
    
    UNION ALL
    
    -- 保留未变化的历史记录
    SELECT
        shop_sk,
        shop_id,
        
        shop_name,
        
        shop_code,
        
        begin_date,
        end_date,
        is_active,
        etl_insert_time,
        etl_update_time
    FROM dim_shop
    WHERE is_active IN (0, 1) AND pt != '${PT_DATE}'
) combined_data
ORDER BY shop_id, begin_date;

-- 清理临时表
DROP TABLE IF EXISTS tmp_dim_shop_new;
DROP TABLE IF EXISTS tmp_dim_shop_changed;


