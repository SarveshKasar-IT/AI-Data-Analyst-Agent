CREATE OR REPLACE VIEW v_seller_analytics AS

SELECT
    seller_id,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(*) AS total_items_sold,

    COUNT(DISTINCT product_id) AS unique_products,

    SUM(price) AS total_product_revenue,

    SUM(freight_value) AS total_freight_revenue,

    SUM(item_total_value) AS total_revenue,

    AVG(price) AS average_product_price,

    AVG(freight_value) AS average_freight_value,

    AVG(item_total_value) AS average_item_value

FROM v_order_analytics

WHERE seller_id IS NOT NULL

GROUP BY seller_id;