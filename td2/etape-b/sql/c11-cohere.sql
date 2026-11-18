-- C11, openrouter:cohere/north-mini-code:free, cell openrouter:cohere/north-mini-code:free:C11
-- copied as-is from traces-td1.csv (value 0, verdict incorrect)
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE
  -- Compute age on 2026-12-01
  (
    -- Age = year difference
    CAST(SUBSTR(c.birth_date, 1, 4) AS INTEGER) -
    CAST(SUBSTR('2026-12-01', 1, 4) AS INTEGER)
  ) =
  CASE
    -- If birthday hasn't occurred yet this year, subtract 1
    WHEN SUBSTR(c.birth_date, 6, 2) || '-' || SUBSTR(c.birth_date, 9, 2) >
         SUBSTR('2026-12-01', 6, 2) || '-' || SUBSTR('2026-12-01', 9, 2)
    THEN 1 ELSE 0 END;
