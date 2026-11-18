SELECT
    c.name AS category_name,
    SUM(t.amount) AS total_amount
FROM transactions AS t
JOIN categories AS c ON c.category_id = t.category_id
WHERE t.currency = {{currency}}
  [[AND {{period}}]]
  AND c.type = 'expense'
GROUP BY c.name
ORDER BY total_amount DESC, category_name;
