import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["order_date", "expected_delivery", "actual_delivery"])
    df["fulfillment_days"] = (df["actual_delivery"] - df["order_date"]).dt.days
    df["delay_days"] = (df["actual_delivery"] - df["expected_delivery"]).dt.days
    df["on_time"] = df["delay_days"] <= 0
    df["fill_rate"] = df["quantity_received"] / df["quantity_ordered"]
    df["stockout"] = df["inventory_level"] == 0
    df["order_value"] = df["quantity_ordered"] * df["unit_cost"]
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def kpi_summary(df: pd.DataFrame) -> dict:
    return {
        "total_orders": len(df),
        "on_time_pct": round(df["on_time"].mean() * 100, 1),
        "avg_fulfillment_days": round(df["fulfillment_days"].mean(), 1),
        "avg_fill_rate": round(df["fill_rate"].mean() * 100, 1),
        "stockout_rate": round(df["stockout"].mean() * 100, 1),
        "total_order_value": round(df["order_value"].sum(), 0),
    }


def supplier_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("supplier")
        .agg(
            orders=("order_id", "count"),
            on_time_pct=("on_time", lambda x: round(x.mean() * 100, 1)),
            avg_delay_days=("delay_days", lambda x: round(x.mean(), 1)),
            delay_std=("delay_days", lambda x: round(x.std(), 1)),
            avg_fill_rate=("fill_rate", lambda x: round(x.mean() * 100, 1)),
        )
        .reset_index()
        .sort_values("on_time_pct")
    )


def monthly_fulfillment(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("month")
        .agg(
            avg_days=("fulfillment_days", "mean"),
            on_time_pct=("on_time", lambda x: x.mean() * 100),
            orders=("order_id", "count"),
        )
        .reset_index()
    )


def inventory_by_category(df: pd.DataFrame) -> pd.DataFrame:
    latest = df.sort_values("order_date").groupby("product").last().reset_index()
    cat = latest.groupby("category").agg(
        avg_inventory=("inventory_level", "mean"),
        stockout_count=("stockout", "sum"),
        products=("product", "count"),
    ).reset_index()
    return cat


def demand_vs_supply(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("month")
        .agg(
            ordered=("quantity_ordered", "sum"),
            received=("quantity_received", "sum"),
        )
        .reset_index()
    )


def fill_rate_by_supplier(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("supplier")
        .agg(fill_rate=("fill_rate", lambda x: round(x.mean() * 100, 1)))
        .reset_index()
        .sort_values("fill_rate")
    )
