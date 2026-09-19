CREATE OR REPLACE VIEW v_revenue_analytics AS

SELECT
    DATE_TRUNC('month', purchase_date) AS revenue_month,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT customer_id) AS total_customers,

    SUM(price) AS product_revenue,

    SUM(freight_value) AS freight_revenue,

    SUM(item_total_value) AS total_revenue,

    AVG(item_total_value) AS average_item_value,

    COUNT(
        DISTINCT CASE
            WHEN order_status = 'delivered'
            THEN order_id
        END
    ) AS delivered_orders,

    COUNT(
        DISTINCT CASE
            WHEN order_status = 'canceled'
            THEN order_id
        END
    ) AS cancelled_orders,

    AVG(
        CASE
            WHEN is_late_delivery IS NOT NULL
            THEN is_late_delivery
        END
    ) AS late_delivery_rate

FROM v_order_analytics

GROUP BY DATE_TRUNC('month', purchase_date)

ORDER BY revenue_month;