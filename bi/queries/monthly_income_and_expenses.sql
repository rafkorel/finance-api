SELECT
    date_trunc('month', t.date)::date AS month,
    c.type AS transaction_type,
    SUM(t.amount) AS total_amount
FROM transactions AS t
JOIN categories AS c ON c.category_id = t.category_id
WHERE t.currency = {{currency}}
  [[AND {{period}}]]
GROUP BY date_trunc('month', t.date)::date, c.type
ORDER BY month, transaction_type;
