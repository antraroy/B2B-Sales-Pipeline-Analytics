"""
Core analytics for the B2B Sales Pipeline project:
KPIs, funnel, forecast, and win-probability model.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

# CSV files are currently stored in the repository root.
# If a data folder exists, this also supports that structure.
if (BASE_DIR / "opportunities.csv").exists():
    DATA = BASE_DIR
else:
    DATA = BASE_DIR / "data"


# =========================================================
# CONSTANTS
# =========================================================

STAGES = [
    "Lead",
    "Qualified",
    "Demo",
    "Proposal",
    "Negotiation",
    "Closed Won",
]

SNAPSHOT = pd.Timestamp("2026-10-31")


# =========================================================
# LOAD DATA
# =========================================================

def load():
    """
    Load opportunities, accounts, and stage history.
    Merge opportunities with account information.
    """

    opportunities_path = DATA / "opportunities.csv"
    accounts_path = DATA / "accounts.csv"
    history_path = DATA / "stage_history.csv"

    # Check that required files exist
    for file_path in [
        opportunities_path,
        accounts_path,
        history_path,
    ]:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required CSV file not found: {file_path}"
            )

    # Load datasets
    opp = pd.read_csv(
        opportunities_path,
        parse_dates=["created_date", "close_date"],
    )

    acc = pd.read_csv(accounts_path)

    hist = pd.read_csv(
        history_path,
        parse_dates=["entered_date"],
    )

    # Merge opportunities and accounts
    df = opp.merge(
        acc,
        on="account_id",
        how="left",
    )

    # Sales cycle duration
    df["cycle_days"] = (
        df["close_date"] - df["created_date"]
    ).dt.days

    # Opportunity creation month
    df["created_month"] = (
        df["created_date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Opportunity closing month
    df["close_month"] = (
        df["close_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df, hist


# =========================================================
# HEADLINE KPIs
# =========================================================

def headline_kpis(df):
    """
    Calculate main sales pipeline KPIs.
    """

    closed = df[df["status"] != "Open"]

    won = df[df["status"] == "Closed Won"]

    open_deals = df[df["status"] == "Open"]

    # Win rate
    if len(closed) > 0:
        win_rate = len(won) / len(closed)
    else:
        win_rate = 0

    # Average won deal size
    avg_deal = (
        won["amount"].mean()
        if not won.empty
        else 0
    )

    # Average sales cycle
    cycle = (
        won["cycle_days"].mean()
        if not won.empty
        else 0
    )

    # Pipeline velocity
    if cycle and cycle > 0:
        pipeline_velocity = (
            len(open_deals)
            * win_rate
            * avg_deal
            / cycle
        )
    else:
        pipeline_velocity = 0

    return {
        "total_opportunities": len(df),

        "win_rate": win_rate,

        "revenue_won": won["amount"].sum(),

        "avg_deal_size": avg_deal,

        "avg_sales_cycle_days": cycle,

        "open_pipeline_value": open_deals["amount"].sum(),

        "pipeline_velocity_per_day": pipeline_velocity,
    }


# =========================================================
# SALES FUNNEL
# =========================================================

def funnel(hist):
    """
    Calculate the number of unique opportunities
    reaching each sales stage.
    """

    reached = (
        hist[hist["stage"].isin(STAGES)]
        .groupby("stage")["opp_id"]
        .nunique()
        .reindex(STAGES, fill_value=0)
    )

    out = reached.rename(
        "opportunities"
    ).to_frame()

    # Conversion from previous stage
    out["conv_from_prev"] = (
        out["opportunities"]
        / out["opportunities"].shift(1)
    )

    # Conversion from first stage
    first_stage_count = out["opportunities"].iloc[0]

    if first_stage_count > 0:
        out["conv_from_top"] = (
            out["opportunities"]
            / first_stage_count
        )
    else:
        out["conv_from_top"] = 0

    out["conv_from_prev"] = (
        out["conv_from_prev"].fillna(0).round(3)
    )

    out["conv_from_top"] = (
        out["conv_from_top"].fillna(0).round(3)
    )

    return out.reset_index()


# =========================================================
# WIN RATE BY CATEGORY
# =========================================================

def win_rate_by(df, col):
    """
    Calculate closed deals, wins, revenue, and win rate
    for a selected category.
    """

    closed = df[df["status"] != "Open"].copy()

    if closed.empty:
        return pd.DataFrame(
            columns=[
                col,
                "closed_deals",
                "won",
                "revenue",
                "win_rate",
            ]
        )

    closed["is_won"] = (
        closed["status"] == "Closed Won"
    )

    grouped = closed.groupby(col).agg(
        closed_deals=("opp_id", "count"),
        won=("is_won", "sum"),
    )

    # Revenue from Closed Won deals only
    revenue = (
        closed[closed["status"] == "Closed Won"]
        .groupby(col)["amount"]
        .sum()
    )

    grouped["revenue"] = revenue

    grouped["revenue"] = (
        grouped["revenue"].fillna(0)
    )

    grouped["win_rate"] = (
        grouped["won"]
        / grouped["closed_deals"]
    ).round(3)

    return (
        grouped
        .sort_values("win_rate", ascending=False)
        .reset_index()
    )


# =========================================================
# MONTHLY REVENUE
# =========================================================

def monthly_revenue(df):
    """
    Calculate revenue from won deals by closing month.
    """

    won = df[df["status"] == "Closed Won"].copy()

    if won.empty:
        return pd.DataFrame(
            columns=["close_month", "revenue"]
        )

    result = (
        won.groupby("close_month")["amount"]
        .sum()
        .reset_index(name="revenue")
    )

    return result.sort_values("close_month")


# =========================================================
# STAGE DURATION ANALYSIS
# =========================================================

def stage_durations(hist):
    """
    Calculate average days spent in each sales stage.
    """

    h = hist.sort_values(
        ["opp_id", "entered_date"]
    ).copy()

    # Next stage date
    h["next_date"] = (
        h.groupby("opp_id")["entered_date"]
        .shift(-1)
    )

    # Duration in current stage
    h["days_in_stage"] = (
        h["next_date"] - h["entered_date"]
    ).dt.days

    result = (
        h[h["stage"].isin(STAGES[:-1])]
        .groupby("stage")["days_in_stage"]
        .mean()
        .reindex(STAGES[:-1])
        .round(1)
        .reset_index()
    )

    return result


# =========================================================
# WEIGHTED SALES FORECAST
# =========================================================

def weighted_forecast(df, hist):
    """
    Calculate weighted pipeline value using historical
    stage-wise probability of winning.
    """

    # Latest stage for each opportunity
    last_stage = (
        hist.sort_values("entered_date")
        .groupby("opp_id")["stage"]
        .last()
    )

    # IDs of won deals
    ever_won = (
        hist[hist["stage"] == "Closed Won"]
        ["opp_id"]
        .unique()
    )

    # Closed opportunities
    closed_ids = df[
        df["status"] != "Open"
    ]["opp_id"]

    # Opportunities that reached stages and are closed
    reached = hist[
        hist["opp_id"].isin(closed_ids)
        & hist["stage"].isin(STAGES)
    ]

    stage_probability = {}

    # Calculate historical win probability per stage
    for stage in STAGES[:-1]:

        stage_ids = (
            reached[reached["stage"] == stage]
            ["opp_id"]
            .unique()
        )

        if len(stage_ids) > 0:
            probability = (
                np.isin(stage_ids, ever_won).mean()
            )
        else:
            probability = 0

        stage_probability[stage] = probability

    # Open deals
    open_deals = df[
        df["status"] == "Open"
    ].copy()

    # Assign stage probability
    open_deals["win_prob"] = (
        open_deals["current_stage"]
        .map(stage_probability)
        .fillna(0)
    )

    # Weighted pipeline
    open_deals["weighted_value"] = (
        open_deals["amount"]
        * open_deals["win_prob"]
    )

    probabilities = pd.Series(
        stage_probability,
        name="stage_win_probability",
    )

    return open_deals, probabilities


# =========================================================
# MACHINE LEARNING WIN-PROBABILITY MODEL
# =========================================================

def win_model(df):
    """
    Train logistic regression on closed deals and
    predict win probability for open opportunities.
    """

    features = [
        "lead_source",
        "industry",
        "region",
        "segment",
        "owner",
    ]

    closed = df[
        df["status"] != "Open"
    ].copy()

    open_deals = df[
        df["status"] == "Open"
    ].copy()

    # If insufficient training data
    if (
        closed.empty
        or closed["status"].nunique() < 2
        or open_deals.empty
    ):
        open_deals["win_score"] = np.nan

        auc = np.nan

        coefficients = pd.Series(
            dtype=float,
            name="coefficient",
        )

        return open_deals, auc, coefficients

    # Prepare categorical variables
    X = pd.get_dummies(
        closed[features + ["amount"]],
        columns=features,
        drop_first=True,
    )

    # Log-transform deal amount
    X["amount"] = np.log1p(
        X["amount"].clip(lower=0)
    )

    y = (
        closed["status"] == "Closed Won"
    ).astype(int)

    # Check if both classes have enough examples
    class_counts = y.value_counts()

    if (
        len(class_counts) < 2
        or class_counts.min() < 2
    ):
        model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
        )

        model.fit(X, y)

        auc = np.nan

    else:
        # Train/test split
        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.25,
                random_state=42,
                stratify=y,
            )
        )

        model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
        )

        model.fit(X_train, y_train)

        # ROC-AUC
        predictions = model.predict_proba(
            X_test
        )[:, 1]

        if y_test.nunique() == 2:
            auc = roc_auc_score(
                y_test,
                predictions,
            )
        else:
            auc = np.nan

    # Prepare open opportunities
    X_open = pd.get_dummies(
        open_deals[features + ["amount"]],
        columns=features,
        drop_first=True,
    )

    X_open["amount"] = np.log1p(
        X_open["amount"].clip(lower=0)
    )

    # Align open data with model columns
    X_open = X_open.reindex(
        columns=X.columns,
        fill_value=0,
    )

    # Predict probability of winning
    open_deals["win_score"] = (
        model.predict_proba(X_open)[:, 1]
        .round(3)
    )

    # Model coefficients
    coefficients = pd.Series(
        model.coef_[0],
        index=X.columns,
    ).sort_values()

    # Sort highest probability first
    open_deals = open_deals.sort_values(
        "win_score",
        ascending=False,
    )

    return open_deals, auc, coefficients


# =========================================================
# TEST RUN
# =========================================================

if __name__ == "__main__":

    df, hist = load()

    print("\n===== HEADLINE KPIs =====")

    for key, value in headline_kpis(df).items():
        print(f"{key}: {value:,.2f}")

    print("\n===== FUNNEL =====")
    print(funnel(hist))

    print("\n===== WIN RATE BY LEAD SOURCE =====")
    print(win_rate_by(df, "lead_source"))

    print("\n===== WIN RATE BY SALES REP =====")
    print(win_rate_by(df, "owner"))

    print("\n===== STAGE DURATIONS =====")
    print(stage_durations(hist))

    print("\n===== WEIGHTED FORECAST =====")

    open_deals, probabilities = weighted_forecast(
        df,
        hist,
    )

    print(
        "Open pipeline:",
        f"{open_deals['amount'].sum():,.0f}",
    )

    print(
        "Weighted forecast:",
        f"{open_deals['weighted_value'].sum():,.0f}",
    )

    print("\n===== MACHINE LEARNING MODEL =====")

    scored, auc, coefficients = win_model(df)

    print("ROC-AUC:", auc)

    print(scored.head(10))
