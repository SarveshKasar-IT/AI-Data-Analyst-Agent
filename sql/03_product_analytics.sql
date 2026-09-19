CREATE OR REPLACE VIEW v_product_analytics AS

SELECT
    product_id,

    product_category_name,

    COUNT(DISTINCT order_id) AS total_orders,

    COUNT(*) AS units_sold,

    COUNT(DISTINCT seller_id) AS number_of_sellers,

    SUM(price) AS total_product_revenue,

    SUM(freight_value) AS total_freight_revenue,

    SUM(item_total_value) AS total_revenue,

    AVG(price) AS average_price,

    AVG(freight_value) AS average_freight_value,

    MIN(price) AS minimum_price,

    MAX(price) AS maximum_price

FROM v_order_analytics

GROUP BY
    product_id,
    product_category_name;