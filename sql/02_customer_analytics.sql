CREATE OR REPLACE VIEW v_customer_analytics AS

SELECT
    customer_id,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(DISTINCT product_id) AS unique_products,

    SUM(price) AS total_product_value,

    SUM(freight_value) AS total_freight_value,

    SUM(item_total_value) AS total_spend,

    AVG(item_total_value) AS average_item_value,

    MIN(purchase_date) AS first_purchase_date,

    MAX(purchase_date) AS last_purchase_date,

    COUNT(
        CASE
            WHEN order_status = 'delivered'
            THEN 1
        END
    ) AS delivered_orders,

    COUNT(
        CASE
            WHEN order_status = 'canceled'
            THEN 1
        END
    ) AS cancelled_orders,

    AVG(
        CASE
            WHEN is_late_delivery IS NOT NULL
            THEN is_late_delivery
        END
    ) AS late_delivery_rate

FROM v_order_analytics

GROUP BY customer_id;