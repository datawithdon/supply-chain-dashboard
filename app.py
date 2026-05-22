import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from utils.metrics import (
    load_data,
    kpi_summary,
    supplier_performance,
    monthly_fulfillment,
    inventory_by_category,
    demand_vs_supply,
    fill_rate_by_supplier,
)

st.set_page_config(
    page_title="Supply Chain Health Dashboard",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Supply Chain Health Dashboard")
st.caption("Upload your own CSV or explore with the built-in sample dataset.")

# ── Sidebar: data source ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Data Source")
    uploaded = st.file_uploader("Upload orders CSV", type="csv")
    st.divider()
    st.markdown(
        "**Required columns:** `order_id`, `product`, `category`, `supplier`, "
        "`order_date`, `expected_delivery`, `actual_delivery`, "
        "`quantity_ordered`, `quantity_received`, `inventory_level`, `unit_cost`"
    )
    st.divider()
    st.header("Filters")

SAMPLE_PATH = Path(__file__).parent / "data" / "sample_orders.csv"

@st.cache_data(show_spinner="Loading data…")
def get_data(file) -> pd.DataFrame:
    src = file if file is not None else SAMPLE_PATH
    return load_data(src)

try:
    df_raw = get_data(uploaded)
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    categories = ["All"] + sorted(df_raw["category"].unique().tolist())
    selected_cat = st.selectbox("Category", categories)

    suppliers = ["All"] + sorted(df_raw["supplier"].unique().tolist())
    selected_sup = st.selectbox("Supplier", suppliers)

    months = sorted(df_raw["month"].unique().tolist())
    date_range = st.select_slider("Month range", options=months, value=(months[0], months[-1]))

df = df_raw.copy()
if selected_cat != "All":
    df = df[df["category"] == selected_cat]
if selected_sup != "All":
    df = df[df["supplier"] == selected_sup]
df = df[(df["month"] >= date_range[0]) & (df["month"] <= date_range[1])]

if df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
kpis = kpi_summary(df)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Orders", f"{kpis['total_orders']:,}")
c2.metric("On-Time Rate", f"{kpis['on_time_pct']}%")
c3.metric("Avg Fulfillment", f"{kpis['avg_fulfillment_days']} days")
c4.metric("Fill Rate", f"{kpis['avg_fill_rate']}%")
c5.metric("Stockout Rate", f"{kpis['stockout_rate']}%")
c6.metric("Order Value", f"${kpis['total_order_value']:,.0f}")

st.divider()

# ── Row 1: Fulfillment trend + Demand vs Supply ───────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Monthly Fulfillment Time")
    mf = monthly_fulfillment(df)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mf["month"], y=mf["orders"], name="Orders", yaxis="y2",
        marker_color="rgba(99,110,250,0.25)", hovertemplate="%{y} orders<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=mf["month"], y=mf["avg_days"].round(1), name="Avg Days",
        mode="lines+markers", line=dict(color="#636EFA", width=2),
        hovertemplate="%{y:.1f} days<extra></extra>",
    ))
    fig.update_layout(
        yaxis=dict(title="Avg Fulfillment Days"),
        yaxis2=dict(title="Order Count", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=10, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Demand vs Supply (Qty)")
    dvs = demand_vs_supply(df)
    fig2 = px.bar(
        dvs, x="month", y=["ordered", "received"],
        barmode="group",
        labels={"value": "Units", "variable": ""},
        color_discrete_map={"ordered": "#EF553B", "received": "#00CC96"},
    )
    fig2.update_layout(margin=dict(t=10, b=10), hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Supplier performance + Fill rate ───────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Supplier Reliability")
    sp = supplier_performance(df)
    fig3 = px.scatter(
        sp, x="avg_delay_days", y="on_time_pct",
        size="orders", color="delay_std",
        hover_name="supplier",
        hover_data={"orders": True, "avg_fill_rate": True, "delay_std": True},
        labels={
            "avg_delay_days": "Avg Delay (days)",
            "on_time_pct": "On-Time Rate (%)",
            "delay_std": "Delay Std Dev",
        },
        color_continuous_scale="RdYlGn_r",
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig3.add_hline(y=80, line_dash="dash", line_color="gray", opacity=0.5,
                   annotation_text="80% target", annotation_position="bottom right")
    fig3.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("Fill Rate by Supplier")
    fr = fill_rate_by_supplier(df)
    colors = ["#EF553B" if v < 90 else "#00CC96" for v in fr["fill_rate"]]
    fig4 = go.Figure(go.Bar(
        x=fr["fill_rate"], y=fr["supplier"], orientation="h",
        marker_color=colors,
        text=fr["fill_rate"].astype(str) + "%",
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig4.add_vline(x=90, line_dash="dot", line_color="gray",
                   annotation_text="90% target", annotation_position="top left")
    fig4.update_layout(margin=dict(t=10, b=10, l=10), xaxis_range=[0, 115])
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Inventory by category + On-time heatmap ───────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("Inventory Health by Category")
    inv = inventory_by_category(df)
    fig5 = px.treemap(
        inv, path=["category"], values="avg_inventory",
        color="stockout_count",
        color_continuous_scale="RdYlGn_r",
        hover_data={"stockout_count": True, "products": True},
        labels={"stockout_count": "Stockouts", "avg_inventory": "Avg Inventory"},
    )
    fig5.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig5, use_container_width=True)

with col_f:
    st.subheader("On-Time Rate by Supplier × Month")
    pivot = (
        df.groupby(["supplier", "month"])["on_time"]
        .mean()
        .mul(100)
        .round(1)
        .reset_index()
        .pivot(index="supplier", columns="month", values="on_time")
    )
    fig6 = px.imshow(
        pivot, color_continuous_scale="RdYlGn", zmin=0, zmax=100,
        labels=dict(color="On-Time %"),
        aspect="auto",
    )
    fig6.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig6, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("Raw Data", expanded=False):
    st.dataframe(
        df.drop(columns=["month"]).sort_values("order_date", ascending=False),
        use_container_width=True,
        height=350,
    )
    csv = df.to_csv(index=False).encode()
    st.download_button("Download filtered CSV", csv, "filtered_orders.csv", "text/csv")
