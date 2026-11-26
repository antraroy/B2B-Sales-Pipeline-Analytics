"""Generate a realistic synthetic B2B SaaS sales dataset (accounts, opportunities, stage history)."""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

STAGES = ["Lead", "Qualified", "Demo", "Proposal", "Negotiation", "Closed Won"]
INDUSTRIES = ["IT Services", "Manufacturing", "Healthcare", "BFSI", "Retail", "Logistics", "Education"]
REGIONS = ["North", "South", "East", "West"]
SEGMENTS = {"SMB": (3_000, 15_000), "Mid-Market": (15_000, 60_000), "Enterprise": (60_000, 250_000)}
SOURCES = {  # (weight, quality multiplier on stage progression)
    "Referral": (0.15, 1.25), "Inbound Web": (0.25, 1.05), "Webinar": (0.15, 1.0),
    "LinkedIn Outreach": (0.20, 0.9), "Cold Call": (0.15, 0.75), "Partner": (0.10, 1.15),
}
REPS = [f"Rep_{c}" for c in "ABCDEFGH"]
REP_SKILL = dict(zip(REPS, [1.2, 1.1, 1.05, 1.0, 1.0, 0.95, 0.9, 0.8]))
BASE_PROGRESS = [0.62, 0.68, 0.62, 0.72, 0.62]  # probability of moving to the next stage
STAGE_GAP_DAYS = [6, 12, 15, 18, 14]


def main(n_accounts=700, n_opps=2400):
    accounts = pd.DataFrame({
        "account_id": [f"ACC{i:04d}" for i in range(n_accounts)],
        "company": [f"Company {i:04d}" for i in range(n_accounts)],
        "industry": rng.choice(INDUSTRIES, n_accounts),
        "region": rng.choice(REGIONS, n_accounts),
        "segment": rng.choice(list(SEGMENTS), n_accounts, p=[0.5, 0.35, 0.15]),
    })

    opps, hist = [], []
    start, end = pd.Timestamp("2025-01-01"), pd.Timestamp("2026-10-31")
    span = (end - start).days
    src_names = list(SOURCES)
    src_p = [SOURCES[s][0] for s in src_names]
    seg_mult = {"SMB": 1.1, "Mid-Market": 1.0, "Enterprise": 0.8}

    for i in range(n_opps):
        acc = accounts.iloc[rng.integers(n_accounts)]
        src = rng.choice(src_names, p=src_p)
        rep = rng.choice(REPS)
        # 80% spread over the full period, 20% recent (builds a live open pipeline)
        created = start + pd.Timedelta(days=int(rng.integers(span - 90, span) if rng.random() < 0.2 else rng.integers(0, span)))
        lo, hi = SEGMENTS[acc.segment]
        amount = round(float(rng.uniform(lo, hi)), -2)
        q = SOURCES[src][1] * REP_SKILL[rep] * seg_mult[acc.segment]
        oid = f"OPP{i:05d}"

        stage_idx, date, lost = 0, created, False
        hist.append((oid, "Lead", date))
        while stage_idx < len(STAGES) - 1:
            gap = max(1, int(rng.normal(STAGE_GAP_DAYS[stage_idx] * (1.3 if acc.segment == "Enterprise" else 1), 3)))
            if date + pd.Timedelta(days=gap) > end:
                break  # still open at snapshot date
            date += pd.Timedelta(days=gap)
            if rng.random() < min(0.97, BASE_PROGRESS[stage_idx] * q):
                stage_idx += 1
                hist.append((oid, STAGES[stage_idx], date))
            else:
                lost = True
                hist.append((oid, "Closed Lost", date))
                break
        if lost:
            status, close = "Closed Lost", date
        elif stage_idx == len(STAGES) - 1:
            status, close = "Closed Won", date
        else:
            status, close = "Open", pd.NaT
        opps.append({
            "opp_id": oid, "account_id": acc.account_id, "owner": rep, "lead_source": src,
            "created_date": created, "close_date": close, "amount": amount,
            "current_stage": STAGES[stage_idx] if status == "Open" else status, "status": status,
        })

    pd.DataFrame(opps).to_csv(OUT / "opportunities.csv", index=False)
    accounts.to_csv(OUT / "accounts.csv", index=False)
    pd.DataFrame(hist, columns=["opp_id", "stage", "entered_date"]).to_csv(OUT / "stage_history.csv", index=False)
    print(f"Saved {len(opps)} opportunities, {n_accounts} accounts, {len(hist)} stage events -> {OUT}")


if __name__ == "__main__":
    main()
