-- Rows counted by the reference and missed by the Cohere and Dots queries (both count nothing)
SELECT c.customer_id, c.birth_date,
       COUNT(*) AS order_lines,
       SUM(o.quantity_product * p.price) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product  p ON o.product_id  = p.product_id
WHERE c.birth_date >  date('2026-12-01', '-26 years')
  AND c.birth_date <= date('2026-12-01', '-25 years')
GROUP BY c.customer_id, c.birth_date
ORDER BY c.customer_id;
