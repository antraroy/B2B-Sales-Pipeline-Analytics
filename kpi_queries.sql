-- 1. Headline KPIs
SELECT COUNT(*) AS total_opps,
       ROUND(100.0 * SUM(CASE WHEN status='Closed Won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN status <> 'Open' THEN 1 ELSE 0 END),0), 1) AS win_rate_pct,
       SUM(CASE WHEN status='Closed Won' THEN amount END) AS revenue_won,
       AVG(CASE WHEN status='Closed Won' THEN amount END) AS avg_deal_size
FROM opportunities;

-- 2. Funnel: unique opportunities reaching each stage
SELECT stage, COUNT(DISTINCT opp_id) AS opps
FROM stage_history
WHERE stage <> 'Closed Lost'
GROUP BY stage
ORDER BY opps DESC;

-- 3. Win rate and revenue by lead source
SELECT lead_source,
       COUNT(*) AS closed_deals,
       SUM(CASE WHEN status='Closed Won' THEN 1 ELSE 0 END) AS won,
       ROUND(100.0 * SUM(CASE WHEN status='Closed Won' THEN 1 ELSE 0 END) / COUNT(*), 1) AS win_rate_pct,
       SUM(CASE WHEN status='Closed Won' THEN amount ELSE 0 END) AS revenue
FROM opportunities
WHERE status <> 'Open'
GROUP BY lead_source
ORDER BY win_rate_pct DESC;

-- 4. Rep leaderboard with rank (window function)
SELECT owner,
       SUM(CASE WHEN status='Closed Won' THEN amount ELSE 0 END) AS revenue,
       RANK() OVER (ORDER BY SUM(CASE WHEN status='Closed Won' THEN amount ELSE 0 END) DESC) AS revenue_rank
FROM opportunities
GROUP BY owner;

-- 5. Monthly revenue with month-over-month growth (CTE + LAG)
WITH monthly AS (
    SELECT SUBSTR(CAST(close_date AS CHAR), 1, 7) AS month, SUM(amount) AS revenue
    FROM opportunities WHERE status='Closed Won'
    GROUP BY SUBSTR(CAST(close_date AS CHAR), 1, 7)
)
SELECT month, revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly ORDER BY month;

-- 6. Avg days spent in each stage (LEAD over stage history)
WITH s AS (
    SELECT opp_id, stage, entered_date,
           LEAD(entered_date) OVER (PARTITION BY opp_id ORDER BY entered_date) AS next_date
    FROM stage_history
)
SELECT stage, ROUND(AVG(next_date - entered_date), 1) AS avg_days_in_stage
FROM s WHERE next_date IS NOT NULL
GROUP BY stage;

-- 7. Stalled deals: open opportunities with no stage movement in 30+ days
SELECT o.opp_id, o.owner, o.current_stage, o.amount,
       MAX(h.entered_date) AS last_move
FROM opportunities o JOIN stage_history h ON h.opp_id = o.opp_id
WHERE o.status = 'Open'
GROUP BY o.opp_id, o.owner, o.current_stage, o.amount
HAVING MAX(h.entered_date) < DATE '2026-10-31' - INTERVAL '30' DAY
ORDER BY o.amount DESC;
