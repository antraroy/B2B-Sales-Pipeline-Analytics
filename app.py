"""Streamlit dashboard: B2B Sales Pipeline Analytics. Run: streamlit run app.py"""
import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (funnel, headline_kpis, load, monthly_revenue, stage_durations,
                          weighted_forecast, win_model, win_rate_by)

st.set_page_config(page_title="B2B Sales Pipeline Analytics", page_icon="📈", layout="wide")


@st.cache_data
def get_data():
    return load()


df_all, hist_all = get_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
def opts(col): return sorted(df_all[col].unique())
region = st.sidebar.multiselect("Region", opts("region"), default=opts("region"))
segment = st.sidebar.multiselect("Segment", opts("segment"), default=opts("segment"))
industry = st.sidebar.multiselect("Industry", opts("industry"), default=opts("industry"))
source = st.sidebar.multiselect("Lead source", opts("lead_source"), default=opts("lead_source"))

df = df_all[df_all.region.isin(region) & df_all.segment.isin(segment)
            & df_all.industry.isin(industry) & df_all.lead_source.isin(source)]
hist = hist_all[hist_all.opp_id.isin(df.opp_id)]

st.title("📈 B2B Sales Pipeline Analytics")
st.caption("Funnel conversion, win-rate drivers, rep performance, weighted forecast and a win-probability model.")

if df.empty or (df.status != "Open").sum() == 0:
    st.warning("No closed deals for the selected filters.")
    st.stop()

k = headline_kpis(df)
c = st.columns(5)
c[0].metric("Revenue won", f"${k['revenue_won']/1e6:,.2f}M")
c[1].metric("Win rate", f"{k['win_rate']:.1%}")
c[2].metric("Avg deal size", f"${k["avg_deal_size"]:,.0f}")
c[3].metric("Avg sales cycle", f"{k['avg_sales_cycle_days']:.0f} days")
c[4].metric("Open pipeline", f"${k["open_pipeline_value"]/1e6:,.2f}M")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Funnel", "Win-rate drivers", "Reps", "Forecast", "Deal scoring (ML)"])

with tab1:
    f = funnel(hist)
    l, r = st.columns(2)
    l.plotly_chart(px.funnel(f, x="opportunities", y="stage", title="Pipeline funnel"), use_container_width=True)
    r.plotly_chart(px.bar(stage_durations(hist), x="stage", y="days_in_stage",
                          title="Avg days spent in each stage"), use_container_width=True)
    st.dataframe(f, use_container_width=True, hide_index=True)
    st.plotly_chart(px.line(monthly_revenue(df), x="close_month", y="revenue", markers=True,
                            title="Monthly revenue won"), use_container_width=True)

with tab2:
    dim = st.selectbox("Break down win rate by", ["lead_source", "industry", "region", "segment"])
    w = win_rate_by(df, dim)
    st.plotly_chart(px.bar(w, x=dim, y="win_rate", text="win_rate", title=f"Win rate by {dim}"),
                    use_container_width=True)
    st.dataframe(w, use_container_width=True, hide_index=True)

with tab3:
    w = win_rate_by(df, "owner")
    st.plotly_chart(px.scatter(w, x="win_rate", y="revenue", size="closed_deals", text="owner",
                               title="Rep performance: win rate vs revenue"), use_container_width=True)
    st.dataframe(w, use_container_width=True, hide_index=True)

with tab4:
    op, p = weighted_forecast(df, hist)
    m = st.columns(2)
    m[0].metric("Open pipeline (unweighted)", f"{op.amount.sum():,.0f}")
    m[1].metric("Weighted forecast", f"{op.weighted_value.sum():,.0f}")
    by_stage = op.groupby("current_stage")[["amount", "weighted_value"]].sum().reset_index()
    st.plotly_chart(px.bar(by_stage, x="current_stage", y=["amount", "weighted_value"], barmode="group",
                           title="Open pipeline by stage: raw vs weighted"), use_container_width=True)
    st.caption("Weight = historical probability that a deal in that stage eventually closes won.")

with tab5:
    scored, auc, coefs = win_model(df_all)
    st.write(f"Logistic regression on closed deals · hold-out ROC-AUC **{auc:.2f}**")
    top = scored[scored.opp_id.isin(df.opp_id)][
        ["opp_id", "owner", "lead_source", "segment", "current_stage", "amount", "win_score"]].head(25)
    st.subheader("Top open deals to prioritise")
    st.dataframe(top, use_container_width=True, hide_index=True)
    st.subheader("What drives winning (model coefficients)")
    st.plotly_chart(px.bar(coefs.reset_index(), x=0, y="index", orientation="h",
                           labels={"0": "coefficient", "index": "feature"}), use_container_width=True)
