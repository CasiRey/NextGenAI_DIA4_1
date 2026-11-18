-- Range of the left-hand side of the Cohere WHERE (birth year - 2026)
SELECT MIN(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) - 2026) AS min_lhs,
       MAX(CAST(SUBSTR(birth_date, 1, 4) AS INTEGER) - 2026) AS max_lhs
FROM customers;
