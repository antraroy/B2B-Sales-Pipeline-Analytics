-- Star-style schema (works in MySQL / PostgreSQL / SQLite; load the CSVs from /data)
CREATE TABLE accounts (
    account_id VARCHAR(10) PRIMARY KEY,
    company    VARCHAR(50),
    industry   VARCHAR(30),
    region     VARCHAR(10),
    segment    VARCHAR(15)
);

CREATE TABLE opportunities (
    opp_id        VARCHAR(10) PRIMARY KEY,
    account_id    VARCHAR(10) REFERENCES accounts(account_id),
    owner         VARCHAR(10),
    lead_source   VARCHAR(30),
    created_date  DATE,
    close_date    DATE,
    amount        DECIMAL(12,2),
    current_stage VARCHAR(20),
    status        VARCHAR(15)      -- Open / Closed Won / Closed Lost
);

CREATE TABLE stage_history (
    opp_id       VARCHAR(10) REFERENCES opportunities(opp_id),
    stage        VARCHAR(20),
    entered_date DATE
);
