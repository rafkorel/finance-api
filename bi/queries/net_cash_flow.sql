SELECT COALESCE(SUM(
    CASE c.type
        WHEN 'income' THEN t.amount
        WHEN 'expense' THEN -t.amount
    END
), 0) AS net_cash_flow
FROM transactions AS t
JOIN categories AS c ON c.category_id = t.category_id
WHERE t.currency = {{currency}}
  [[AND {{period}}]];
