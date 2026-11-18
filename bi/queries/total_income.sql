SELECT COALESCE(SUM(t.amount), 0) AS total_income
FROM transactions AS t
JOIN categories AS c ON c.category_id = t.category_id
WHERE t.currency = {{currency}}
  [[AND {{period}}]]
  AND c.type = 'income';
