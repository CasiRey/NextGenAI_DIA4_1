-- C11 reference: aged 25 on 2026-12-01 = born from 2000-12-02 to 2001-12-01 inclusive
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product  p ON o.product_id  = p.product_id
WHERE c.birth_date >  date('2026-12-01', '-26 years')
  AND c.birth_date <= date('2026-12-01', '-25 years');
