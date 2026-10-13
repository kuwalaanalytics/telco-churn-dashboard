"""Step 1 and 2: profile the raw Telco churn file, clean it, and add features.

Run from the project root:  python src/prepare.py
Outputs:
  data/clean/telco_churn_clean.csv
  data/clean/data_profile.json   (schema summary and cleaning log)
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUT_DIR = ROOT / "data" / "clean"

ADDONS = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
          "StreamingTV", "StreamingMovies"]
TENURE_BANDS = ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49-72 months"]
CHARGE_BANDS = ["Under $30", "$30-49", "$50-69", "$70-89", "$90+"]


def profile(df: pd.DataFrame) -> dict:
    blanks = {c: int((df[c].astype(str).str.strip() == "").sum()) for c in df.columns}
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "nulls": {c: int(n) for c, n in df.isna().sum().items() if n},
        "blank_strings": {c: n for c, n in blanks.items() if n},
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_customer_ids": int(df["customerID"].duplicated().sum()),
        "unique_values": {c: sorted(map(str, df[c].unique()))
                          for c in df.columns if df[c].nunique() <= 6},
    }


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    log = []
    df = df.copy()

    # Text columns: trim stray whitespace.
    obj = df.select_dtypes(exclude="number").columns
    df[obj] = df[obj].apply(lambda s: s.str.strip())

    # TotalCharges arrives as text. Blank values belong to brand new customers.
    blank = df["TotalCharges"] == ""
    all_new = bool((df.loc[blank, "tenure"] == 0).all())
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0.0)
    log.append(
        f"TotalCharges converted from text to number. {int(blank.sum())} blank values found; "
        f"all have tenure 0 ({all_new}), meaning new customers not yet billed, so they were "
        "set to 0 rather than dropped."
    )

    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    log.append("SeniorCitizen recoded from 0/1 to No/Yes to match the other Yes/No columns.")

    df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)
    log.append("ChurnFlag added (1 = churned, 0 = stayed) for calculations.")

    n_before = len(df)
    df = df.drop_duplicates(subset="customerID")
    log.append(f"Duplicate customer IDs removed: {n_before - len(df)}.")

    # Features
    df["TenureBand"] = pd.cut(df["tenure"], [-1, 6, 12, 24, 48, 72], labels=TENURE_BANDS).astype(str)
    df["MonthlyChargeBand"] = pd.cut(df["MonthlyCharges"], [0, 30, 50, 70, 90, np.inf],
                                     right=False, labels=CHARGE_BANDS).astype(str)
    log.append("TenureBand: 0-6, 7-12, 13-24, 25-48, 49-72 months.")
    log.append("MonthlyChargeBand: under $30, $30-49, $50-69, $70-89, $90+.")

    df["HasInternet"] = (df["InternetService"] != "No").map({True: "Yes", False: "No"})
    df["NumAddOns"] = (df[ADDONS] == "Yes").sum(axis=1)
    df["NumServices"] = (
        (df["PhoneService"] == "Yes").astype(int)
        + (df["MultipleLines"] == "Yes").astype(int)
        + (df["HasInternet"] == "Yes").astype(int)
        + df["NumAddOns"]
    )
    df["NoAddOns"] = (df["NumAddOns"] == 0).map({True: "Yes", False: "No"})
    log.append("NumServices: count of phone, multiple lines, internet and the six add-ons (0 to 9).")
    log.append("NumAddOns / NoAddOns: add-ons are online security, online backup, device protection, "
               "tech support, streaming TV and streaming movies. Customers without internet cannot "
               "buy these, so add-on comparisons are made among internet customers only.")
    return df, log


def main():
    raw = pd.read_csv(RAW)
    prof = profile(raw)
    df, log = clean(raw)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / "telco_churn_clean.csv", index=False)
    prof["cleaning_log"] = log
    prof["clean_rows"] = int(len(df))
    prof["clean_columns"] = list(df.columns)
    (OUT_DIR / "data_profile.json").write_text(json.dumps(prof, indent=2))
    print(json.dumps(prof, indent=2))


if __name__ == "__main__":
    main()
