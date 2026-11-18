WITH movements AS (
    SELECT
        date,
        from_account_id AS account_id,
        amount,
        from_currency AS currency,
        'outgoing' AS direction
    FROM transfers

    UNION ALL

    SELECT
        date,
        to_account_id,
        credited_amount,
        to_currency,
        'incoming'
    FROM transfers
)
SELECT
    a.name AS account_name,
    m.direction,
    SUM(m.amount) AS total_amount
FROM movements AS m
JOIN accounts AS a ON a.account_id = m.account_id
WHERE m.currency = {{currency}}
  [[AND {{period}}]]
GROUP BY a.account_id, a.name, m.direction
ORDER BY account_name, m.direction;
