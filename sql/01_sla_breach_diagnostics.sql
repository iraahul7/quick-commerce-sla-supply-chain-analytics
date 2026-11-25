-- ============================================================================
-- 01_sla_breach_diagnostics.sql
-- Diagnosing 15-Minute Quick-Commerce Delivery SLA Breaches Across Dark Stores
-- Author: Rahul
-- ============================================================================

WITH delivery_metrics AS (
    SELECT
        order_id,
        city,
        dark_store_id,
        order_hour,
        dispatch_delay_mins,
        transit_time_mins,
        (dispatch_delay_mins + transit_time_mins) AS total_delivery_mins,
        CASE 
            WHEN (dispatch_delay_mins + transit_time_mins) > 15.0 THEN 1 
            ELSE 0 
        END AS is_sla_breach
    FROM fact_quick_commerce_orders
    WHERE order_status = 'DELIVERED'
),
store_summary AS (
    SELECT
        city,
        dark_store_id,
        COUNT(order_id) AS total_orders,
        SUM(is_sla_breach) AS breached_orders,
        ROUND(AVG(is_sla_breach) * 100.0, 2) AS sla_breach_rate_pct,
        ROUND(AVG(dispatch_delay_mins), 2) AS avg_picker_dispatch_mins,
        ROUND(AVG(transit_time_mins), 2) AS avg_rider_transit_mins,
        RANK() OVER (PARTITION BY city ORDER BY AVG(is_sla_breach) DESC) AS city_risk_rank
    FROM delivery_metrics
    GROUP BY city, dark_store_id
)
SELECT
    city,
    dark_store_id,
    total_orders,
    breached_orders,
    sla_breach_rate_pct,
    avg_picker_dispatch_mins,
    avg_rider_transit_mins
FROM store_summary
WHERE city_risk_rank <= 3
ORDER BY sla_breach_rate_pct DESC;
