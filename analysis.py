"""Core analytics for the B2B Sales Pipeline project: KPIs, funnel, forecast, win-probability model."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

DATA = Path(__file__).resolve().parent.parent / "data"
STAGES = ["Lead", "Qualified", "Demo", "Proposal", "Negotiation", "Closed Won"]
SNAPSHOT = pd.Timestamp("2026-10-31")


def load():
    opp = pd.read_csv(DATA / "opportunities.csv", parse_dates=["created_date", "close_date"])
    acc = pd.read_csv(DATA / "accounts.csv")
    hist = pd.read_csv(DATA / "stage_history.csv", parse_dates=["entered_date"])
    df = opp.merge(acc, on="account_id")
    df["cycle_days"] = (df["close_date"] - df["created_date"]).dt.days
    df["created_month"] = df["created_date"].dt.to_period("M").astype(str)
    df["close_month"] = df["close_date"].dt.to_period("M").astype(str)
    return df, hist


def headline_kpis(df):
    closed = df[df.status != "Open"]
    won = df[df.status == "Closed Won"]
    win_rate = len(won) / len(closed)
    avg_deal = won.amount.mean()
    cycle = won.cycle_days.mean()
    open_ = df[df.status == "Open"]
    return {
        "total_opportunities": len(df),
        "win_rate": win_rate,
        "revenue_won": won.amount.sum(),
        "avg_deal_size": avg_deal,
        "avg_sales_cycle_days": cycle,
        "open_pipeline_value": open_.amount.sum(),
        # Pipeline velocity = (#opps x win rate x avg deal) / cycle length
        "pipeline_velocity_per_day": len(open_) * win_rate * avg_deal / cycle,
    }


def funnel(hist):
    """Unique opportunities that reached each stage + stage-to-stage conversion."""
    reached = hist[hist.stage.isin(STAGES)].groupby("stage").opp_id.nunique().reindex(STAGES)
    out = reached.rename("opportunities").to_frame()
    out["conv_from_prev"] = (out.opportunities / out.opportunities.shift(1)).round(3)
    out["conv_from_top"] = (out.opportunities / out.opportunities.iloc[0]).round(3)
    return out.reset_index()


def win_rate_by(df, col):
    closed = df[df.status != "Open"]
    g = closed.groupby(col).agg(
        closed_deals=("opp_id", "count"),
        won=("status", lambda s: (s == "Closed Won").sum()),
        revenue=("amount", lambda s: s[closed.loc[s.index, "status"] == "Closed Won"].sum()),
    )
    g["win_rate"] = (g.won / g.closed_deals).round(3)
    return g.sort_values("win_rate", ascending=False).reset_index()


def monthly_revenue(df):
    won = df[df.status == "Closed Won"]
    return won.groupby("close_month").amount.sum().reset_index(name="revenue")


def stage_durations(hist):
    h = hist.sort_values(["opp_id", "entered_date"]).copy()
    h["next_date"] = h.groupby("opp_id").entered_date.shift(-1)
    h["days_in_stage"] = (h.next_date - h.entered_date).dt.days
    return h[h.stage.isin(STAGES[:-1])].groupby("stage").days_in_stage.mean().reindex(STAGES[:-1]).round(1).reset_index()


def weighted_forecast(df, hist):
    """Open pipeline value x empirical probability of eventually winning from its current stage."""
    last = hist.sort_values("entered_date").groupby("opp_id").stage.last()
    ever_won = hist[hist.stage == "Closed Won"].opp_id.unique()
    closed_ids = df[df.status != "Open"].opp_id
    reach = hist[hist.opp_id.isin(closed_ids) & hist.stage.isin(STAGES)]
    p = {}
    for st in STAGES[:-1]:
        ids = reach[reach.stage == st].opp_id.unique()
        p[st] = np.isin(ids, ever_won).mean() if len(ids) else 0
    op = df[df.status == "Open"].copy()
    op["win_prob"] = op.current_stage.map(p)
    op["weighted_value"] = op.amount * op.win_prob
    return op, pd.Series(p, name="stage_win_probability")


def win_model(df):
    """Logistic regression predicting win from deal attributes -> scores open deals."""
    feats = ["lead_source", "industry", "region", "segment", "owner"]
    closed = df[df.status != "Open"].copy()
    X = pd.get_dummies(closed[feats + ["amount"]], columns=feats, drop_first=True)
    X["amount"] = np.log1p(X["amount"])
    y = (closed.status == "Closed Won").astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000, class_weight="balanced").fit(Xtr, ytr)
    auc = roc_auc_score(yte, model.predict_proba(Xte)[:, 1])
    op = df[df.status == "Open"].copy()
    Xo = pd.get_dummies(op[feats + ["amount"]], columns=feats, drop_first=True)
    Xo["amount"] = np.log1p(Xo["amount"])
    Xo = Xo.reindex(columns=X.columns, fill_value=0)
    op["win_score"] = model.predict_proba(Xo)[:, 1].round(3)
    coefs = pd.Series(model.coef_[0], index=X.columns).sort_values()
    return op.sort_values("win_score", ascending=False), auc, coefs


if __name__ == "__main__":
    df, hist = load()
    print("== KPIs =="); [print(f"{k}: {v:,.2f}") for k, v in headline_kpis(df).items()]
    print("\n== Funnel =="); print(funnel(hist))
    print("\n== Win rate by lead source =="); print(win_rate_by(df, "lead_source"))
    print("\n== Win rate by rep =="); print(win_rate_by(df, "owner"))
    op, p = weighted_forecast(df, hist)
    print(f"\nOpen pipeline: {op.amount.sum():,.0f} | weighted forecast: {op.weighted_value.sum():,.0f}")
    scored, auc, _ = win_model(df)
    print(f"Win-probability model ROC-AUC: {auc:.3f}")
