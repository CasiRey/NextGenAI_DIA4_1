-- Each condition of the Dots query tested alone
SELECT 'birth_date only', COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date = '2001-12-01'
UNION ALL
SELECT 'order date only', COALESCE(SUM(o.quantity_product * p.price), 0)
FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN product p ON o.product_id = p.product_id
WHERE o.date >= '2026-12-01' AND o.date < '2026-12-02'
UNION ALL
SELECT 'first order', MIN(date) FROM orders
UNION ALL
SELECT 'last order', MAX(date) FROM orders;
