CREATE OR REPLACE VIEW v_order_analytics AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,

    -- Order dates
    CAST(o.order_purchase_timestamp AS TIMESTAMP) AS purchase_date,
    CAST(o.order_approved_at AS TIMESTAMP) AS approved_date,
    CAST(o.order_delivered_carrier_date AS TIMESTAMP) AS delivered_to_carrier_date,
    CAST(o.order_delivered_customer_date AS TIMESTAMP) AS delivered_to_customer_date,
    CAST(o.order_estimated_delivery_date AS TIMESTAMP) AS estimated_delivery_date,

    -- Product and seller
    oi.product_id,
    p.product_category_name,
    oi.seller_id,

    -- Financial metrics
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS item_total_value,

    -- Delivery metrics
    CASE
        WHEN o.order_delivered_customer_date IS NOT NULL
        THEN
            CAST(o.order_delivered_customer_date AS TIMESTAMP)
            - CAST(o.order_purchase_timestamp AS TIMESTAMP)
    END AS delivery_duration,

    CASE
        WHEN o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN
            CASE
                WHEN CAST(o.order_delivered_customer_date AS TIMESTAMP)
                     > CAST(o.order_estimated_delivery_date AS TIMESTAMP)
                THEN 1
                ELSE 0
            END
    END AS is_late_delivery

FROM orders o

LEFT JOIN order_items oi
    ON o.order_id = oi.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id;