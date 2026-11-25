"""
Quick-Commerce & Last-Mile Supply Chain SLA Bottleneck Analytics
Simulates 60,000 dark-store orders across Indian metro hubs and isolates SLA bottlenecks.
Author: Rahul
"""

import sqlite3
import numpy as np
import pandas as pd


def generate_supply_chain_data(n_orders: int = 60000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cities = ["Delhi NCR", "Bengaluru", "Mumbai", "Hyderabad", "Pune"]
    city_col = rng.choice(cities, size=n_orders, p=[0.30, 0.28, 0.22, 0.12, 0.08])
    store_num = rng.integers(1, 7, size=n_orders)
    dark_store_id = [f"{c[:3].upper()}-DS0{s}" for c, s in zip(city_col, store_num)]

    order_hour = rng.choice(range(7, 24), size=n_orders)
    is_peak = np.isin(order_hour, [19, 20, 21])

    dispatch_delay = np.where(
        is_peak,
        rng.normal(loc=6.8, scale=1.9, size=n_orders),
        rng.normal(loc=3.2, scale=1.1, size=n_orders)
    ).clip(1.0, 18.0)

    transit_time = np.where(
        is_peak,
        rng.normal(loc=9.4, scale=2.4, size=n_orders),
        rng.normal(loc=7.1, scale=1.8, size=n_orders)
    ).clip(2.5, 25.0)

    total_mins = np.round(dispatch_delay + transit_time, 2)
    sla_breach = (total_mins > 15.0).astype(int)

    return pd.DataFrame({
        "order_id": range(500001, 500001 + n_orders),
        "city": city_col,
        "dark_store_id": dark_store_id,
        "order_hour": order_hour,
        "is_peak_hour": is_peak.astype(int),
        "dispatch_delay_mins": np.round(dispatch_delay, 2),
        "transit_time_mins": np.round(transit_time, 2),
        "total_delivery_mins": total_mins,
        "is_sla_breach": sla_breach,
        "order_status": "DELIVERED"
    })


def run_sql_diagnostics(df: pd.DataFrame) -> pd.DataFrame:
    conn = sqlite3.connect(":memory:")
    df.to_sql("fact_quick_commerce_orders", conn, index=False)

    query = """
    SELECT
        CASE WHEN is_peak_hour = 1 THEN 'Peak Rush (7-10 PM)' ELSE 'Off-Peak Hours' END AS time_window,
        COUNT(*) AS total_orders,
        ROUND(AVG(dispatch_delay_mins), 2) AS avg_picker_dispatch_mins,
        ROUND(AVG(transit_time_mins), 2) AS avg_rider_transit_mins,
        ROUND(AVG(total_delivery_mins), 2) AS avg_total_mins,
        ROUND(AVG(is_sla_breach) * 100.0, 2) AS sla_breach_rate_pct
    FROM fact_quick_commerce_orders
    GROUP BY is_peak_hour
    ORDER BY sla_breach_rate_pct DESC;
    """
    summary = pd.read_sql_query(query, conn)
    conn.close()
    return summary


if __name__ == "__main__":
    df = generate_supply_chain_data(60000)
    df.to_csv("data/darkstore_deliveries_60k.csv", index=False)
    summary = run_sql_diagnostics(df)
    print("=== Quick-Commerce 15-Min SLA Bottleneck Summary ===")
    print(summary.to_string(index=False))
