"""Prepare and validate the synthetic Diageo portfolio dataset.

Outputs:
  - diageo_sales_powerbi_ready.csv: typed, enriched import table for Power BI.
  - ../work/diageo_records.json: typed records used to build the Excel workbook.
  - ../work/diageo_summary.json: validated aggregates used for QA.

Synthetic portfolio dataset — not official Diageo sales data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "data" / "raw" / "diageo_sales_synthetic_10000.csv"


NUMERIC_COLUMNS = [
    "Year",
    "Month",
    "Units_Sold",
    "Unit_Price_GBP",
    "Discount_Pct",
    "Gross_Revenue_GBP",
    "Net_Revenue_GBP",
    "COGS_GBP",
    "Gross_Profit_GBP",
    "Profit_Margin_Pct",
    "Sales_Target_GBP",
    "Target_Achievement_Pct",
    "YoY_Growth_Simulation_Pct",
]


def json_value(value):
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).strftime("%Y-%m-%d")
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return None if np.isnan(value) else float(value)
    if pd.isna(value):
        return None
    return value


def records(df: pd.DataFrame) -> list[dict]:
    return [
        {key: json_value(value) for key, value in row.items()}
        for row in df.to_dict(orient="records")
    ]


def aggregate(df: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(dimensions, dropna=False)
        .agg(
            Transactions=("Transaction_ID", "nunique"),
            Units_Sold=("Units_Sold", "sum"),
            Net_Revenue_GBP=("Net_Revenue_GBP", "sum"),
            Gross_Profit_GBP=("Gross_Profit_GBP", "sum"),
            Sales_Target_GBP=("Sales_Target_GBP", "sum"),
            Average_Discount=("Discount_Pct", "mean"),
        )
        .reset_index()
    )
    grouped["Profit_Margin"] = (
        grouped["Gross_Profit_GBP"] / grouped["Net_Revenue_GBP"]
    )
    grouped["Target_Achievement"] = (
        grouped["Net_Revenue_GBP"] / grouped["Sales_Target_GBP"]
    )
    grouped["Target_Variance_GBP"] = (
        grouped["Net_Revenue_GBP"] - grouped["Sales_Target_GBP"]
    )
    grouped["Revenue_per_Transaction"] = (
        grouped["Net_Revenue_GBP"] / grouped["Transactions"]
    )
    grouped["Units_per_Transaction"] = (
        grouped["Units_Sold"] / grouped["Transactions"]
    )
    return grouped


def prepare(source: Path, output_dir: Path, work_dir: Path) -> dict:
    df = pd.read_csv(source)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="raise")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if len(df) != 10_000:
        raise ValueError(f"Expected 10,000 rows; found {len(df):,}")
    if df["Transaction_ID"].nunique() != len(df):
        raise ValueError("Transaction_ID is not unique")
    if int(df.isna().sum().sum()) != 0:
        raise ValueError("Unexpected missing values found")

    # Rebuild reliable date attributes from the authoritative Order_Date.
    df["Year"] = df["Order_Date"].dt.year.astype(int)
    df["Quarter"] = "Q" + df["Order_Date"].dt.quarter.astype(str)
    df["Month"] = df["Order_Date"].dt.month.astype(int)
    df["Month_Name"] = df["Order_Date"].dt.month_name()
    df["Month_Start"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    df["Year_Month"] = df["Order_Date"].dt.strftime("%Y-%m")

    # Row-level helper fields for Power BI. Executive ratios remain measures.
    df["Profit_Margin_Calc"] = np.where(
        df["Net_Revenue_GBP"] != 0,
        df["Gross_Profit_GBP"] / df["Net_Revenue_GBP"],
        np.nan,
    )
    df["Target_Achievement_Calc"] = np.where(
        df["Sales_Target_GBP"] != 0,
        df["Net_Revenue_GBP"] / df["Sales_Target_GBP"],
        np.nan,
    )
    df["Target_Variance_GBP"] = (
        df["Net_Revenue_GBP"] - df["Sales_Target_GBP"]
    )
    df["Target_Variance_Pct"] = np.where(
        df["Sales_Target_GBP"] != 0,
        df["Target_Variance_GBP"] / df["Sales_Target_GBP"],
        np.nan,
    )
    df["Target_Status_Row"] = np.where(
        df["Net_Revenue_GBP"] >= df["Sales_Target_GBP"],
        "Above Target",
        "Below Target",
    )

    # Field order keeps source columns intact and appends curated helpers.
    source_columns = [
        "Transaction_ID",
        "Order_Date",
        "Year",
        "Quarter",
        "Month",
        "Month_Name",
        "Month_Start",
        "Year_Month",
        "Country",
        "Region",
        "Currency",
        "Brand",
        "Category",
        "Channel",
        "Customer_Type",
        "Sales_Rep_ID",
        "Units_Sold",
        "Unit_Price_GBP",
        "Discount_Pct",
        "Gross_Revenue_GBP",
        "Net_Revenue_GBP",
        "COGS_GBP",
        "Gross_Profit_GBP",
        "Profit_Margin_Pct",
        "Sales_Target_GBP",
        "Target_Achievement_Pct",
        "YoY_Growth_Simulation_Pct",
        "Promotion_Flag",
        "Market_Segment",
        "Profit_Margin_Calc",
        "Target_Achievement_Calc",
        "Target_Variance_GBP",
        "Target_Variance_Pct",
        "Target_Status_Row",
    ]
    df = df[source_columns]

    # Financial validation using stored precision.
    net_gap = (
        df["Net_Revenue_GBP"]
        - df["Gross_Revenue_GBP"] * (1 - df["Discount_Pct"])
    ).abs()
    profit_gap = (
        df["Gross_Profit_GBP"]
        - (df["Net_Revenue_GBP"] - df["COGS_GBP"])
    ).abs()
    if float(net_gap.max()) > 0.011:
        raise ValueError("Net revenue reconciliation exceeded £0.01")
    if float(profit_gap.max()) > 0.011:
        raise ValueError("Gross profit reconciliation exceeded £0.01")

    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "diageo_sales_powerbi_ready.csv"
    df.to_csv(csv_path, index=False, date_format="%Y-%m-%d")

    record_path = work_dir / "diageo_records.json"
    record_path.write_text(
        json.dumps({"columns": list(df.columns), "records": records(df)}),
        encoding="utf-8",
    )

    overall = {
        "Transactions": int(df["Transaction_ID"].nunique()),
        "Units_Sold": int(df["Units_Sold"].sum()),
        "Net_Revenue_GBP": float(df["Net_Revenue_GBP"].sum()),
        "Gross_Profit_GBP": float(df["Gross_Profit_GBP"].sum()),
        "Sales_Target_GBP": float(df["Sales_Target_GBP"].sum()),
    }
    overall["Profit_Margin"] = (
        overall["Gross_Profit_GBP"] / overall["Net_Revenue_GBP"]
    )
    overall["Target_Achievement"] = (
        overall["Net_Revenue_GBP"] / overall["Sales_Target_GBP"]
    )
    overall["Target_Variance_GBP"] = (
        overall["Net_Revenue_GBP"] - overall["Sales_Target_GBP"]
    )

    max_date = df["Order_Date"].max()
    current_start = pd.Timestamp(max_date.year, 1, 1)
    prior_start = pd.Timestamp(max_date.year - 1, 1, 1)
    prior_end = max_date - pd.DateOffset(years=1)
    current_ytd = df.loc[
        (df["Order_Date"] >= current_start) & (df["Order_Date"] <= max_date),
        "Net_Revenue_GBP",
    ].sum()
    prior_ytd = df.loc[
        (df["Order_Date"] >= prior_start) & (df["Order_Date"] <= prior_end),
        "Net_Revenue_GBP",
    ].sum()
    overall["Comparable_YTD_Growth"] = float(current_ytd / prior_ytd - 1)
    overall["Max_Data_Date"] = max_date.strftime("%Y-%m-%d")

    summaries = {
        "overall": overall,
        "monthly": records(
            aggregate(df, ["Month_Start"]).sort_values("Month_Start")
        ),
        "brand": records(
            aggregate(df, ["Brand", "Category"]).sort_values(
                "Net_Revenue_GBP", ascending=False
            )
        ),
        "country": records(
            aggregate(df, ["Country", "Region"]).sort_values(
                "Net_Revenue_GBP", ascending=False
            )
        ),
        "channel": records(
            aggregate(df, ["Channel"]).sort_values(
                "Net_Revenue_GBP", ascending=False
            )
        ),
        "category": records(
            aggregate(df, ["Category"]).sort_values(
                "Net_Revenue_GBP", ascending=False
            )
        ),
        "promotion": records(
            aggregate(df, ["Promotion_Flag"]).sort_values("Promotion_Flag")
        ),
        "validation": {
            "rows": int(len(df)),
            "unique_transactions": int(df["Transaction_ID"].nunique()),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "max_net_revenue_gap": float(net_gap.max()),
            "max_gross_profit_gap": float(profit_gap.max()),
        },
    }
    summary_path = work_dir / "diageo_summary.json"
    summary_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")

    return {
        "csv": str(csv_path),
        "records": str(record_path),
        "summary": str(summary_path),
        "overall": overall,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "data" / "processed",
    )
    parser.add_argument(
        "--work-dir", type=Path, default=REPO_ROOT / ".generated"
    )
    args = parser.parse_args()
    result = prepare(args.source, args.output_dir, args.work_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
