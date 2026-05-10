-- ========================================
-- DIM 维度表 ETL SQL 模板
-- ========================================
-- 用于生成 DIM 维度表的加载脚本
-- 支持 SCD Type I 和 Type II 处理


-- ========== SCD Type II: 拉链表(完整历史) ==========
-- 维度值变化时生成新记录，旧记录标记为失效
-- 记录开始日期和结束日期，支持时间维度分析

-- 步骤1：临时表 - 承载最新的DWS数据
DROP TABLE IF EXISTS tmp_dim_customer_new;
CREATE TABLE tmp_dim_customer_new AS
SELECT
    customer_id,
    
    customer_name,
    
    customer_code,
    
    CURRENT_TIMESTAMP() AS etl_time
FROM dws_default_customer_di
WHERE pt = '${PT_DATE}'
    AND is_valid = 1;

-- 步骤2：识别变化的记录
-- 旧记录存在但新值不同 = 发生了变化
DROP TABLE IF EXISTS tmp_dim_customer_changed;
CREATE TABLE tmp_dim_customer_changed AS
SELECT
    old.customer_sk,
    old.customer_id,
    
    old.customer_name,
    
    old.customer_code,
    
    '${PT_DATE}' AS end_date,    -- 旧记录失效时间
    0 AS is_active
FROM dim_customer old
INNER JOIN tmp_dim_customer_new new
    ON old.customer_id = new.customer_id
    AND old.is_active = 1
WHERE
    -- 至少一个属性发生变化
    
    NVL(old.customer_name, '') != NVL(new.customer_name, '')
     OR 
    
    NVL(old.customer_code, '') != NVL(new.customer_code, '')
    
    ;

-- 步骤3：组织最终结果
INSERT OVERWRITE TABLE dim_customer PARTITION (pt='${PT_DATE}')
SELECT 
    customer_sk,
    customer_id,
    
    customer_name,
    
    customer_code,
    
    begin_date,
    end_date,
    is_active,
    etl_insert_time,
    etl_update_time
FROM (
    -- 新增或变化后的新记录
    SELECT
        ROW_NUMBER() OVER (ORDER BY customer_id) + 
            COALESCE(MAX(customer_sk), 0) AS customer_sk,  -- 分配新的SK
        new.customer_id,
        
        new.customer_name,
        
        new.customer_code,
        
        '${PT_DATE}' AS begin_date,
        '9999-12-31' AS end_date,
        1 AS is_active,
        CURRENT_TIMESTAMP() AS etl_insert_time,
        CURRENT_TIMESTAMP() AS etl_update_time
    FROM tmp_dim_customer_new new
    LEFT ANTI JOIN (
        SELECT customer_id FROM dim_customer WHERE is_active = 1
    ) old
        ON new.customer_id = old.customer_id
    
    UNION ALL
    
    -- 已变化的旧记录（标记为失效）
    SELECT 
        *
    FROM tmp_dim_customer_changed
    
    UNION ALL
    
    -- 保留未变化的历史记录
    SELECT
        customer_sk,
        customer_id,
        
        customer_name,
        
        customer_code,
        
        begin_date,
        end_date,
        is_active,
        etl_insert_time,
        etl_update_time
    FROM dim_customer
    WHERE is_active IN (0, 1) AND pt != '${PT_DATE}'
) combined_data
ORDER BY customer_id, begin_date;

-- 清理临时表
DROP TABLE IF EXISTS tmp_dim_customer_new;
DROP TABLE IF EXISTS tmp_dim_customer_changed;


