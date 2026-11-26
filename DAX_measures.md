# Power BI setup

Import `data/opportunities.csv`, `data/accounts.csv`, `data/stage_history.csv`.
Relationships: `accounts[account_id] 1 → * opportunities[account_id]`, `opportunities[opp_id] 1 → * stage_history[opp_id]`.

## Measures
```DAX
Total Opportunities = COUNTROWS(opportunities)
Closed Deals = CALCULATE(COUNTROWS(opportunities), opportunities[status] <> "Open")
Won Deals = CALCULATE(COUNTROWS(opportunities), opportunities[status] = "Closed Won")
Win Rate = DIVIDE([Won Deals], [Closed Deals])
Revenue Won = CALCULATE(SUM(opportunities[amount]), opportunities[status] = "Closed Won")
Avg Deal Size = DIVIDE([Revenue Won], [Won Deals])
Open Pipeline = CALCULATE(SUM(opportunities[amount]), opportunities[status] = "Open")
Avg Sales Cycle (Days) =
    CALCULATE(AVERAGEX(opportunities, DATEDIFF(opportunities[created_date], opportunities[close_date], DAY)),
              opportunities[status] = "Closed Won")
Pipeline Velocity =
    DIVIDE(CALCULATE(COUNTROWS(opportunities), opportunities[status] = "Open") * [Win Rate] * [Avg Deal Size],
           [Avg Sales Cycle (Days)])
```

## Suggested pages
1. **Executive Summary** – KPI cards (Revenue Won, Win Rate, Open Pipeline, Avg Cycle), monthly revenue line.
2. **Funnel & Conversion** – funnel visual by stage, drop-off % between stages.
3. **Source & Segment Performance** – win rate by lead source, industry, region, segment.
4. **Rep Performance** – leaderboard, win rate vs. avg deal size scatter.
5. **Forecast** – open pipeline by stage with weighted value.
