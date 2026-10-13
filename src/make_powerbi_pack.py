"""Optional: prepare the data files for a Power BI version of the dashboard.

Run from the project root:  python src/make_powerbi_pack.py
Reads data/clean/telco_churn_scored.csv and data/clean/findings.json and writes four
CSV files to powerbi/data/. See powerbi/README.md for how to build the report.
"""
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi" / "data"

TENURE_BANDS = ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49-72 months"]
CHARGE_BANDS = ["Under $30", "$30-49", "$50-69", "$70-89", "$90+"]
RISK_BANDS = ["High", "Medium", "Low"]
ADDONS = {"OnlineSecurity": "Online security", "TechSupport": "Tech support",
          "OnlineBackup": "Online backup", "DeviceProtection": "Device protection",
          "StreamingTV": "Streaming TV", "StreamingMovies": "Streaming movies"}
DRIVERS = {"Contract": "Contract type", "tenure": "Tenure", "TotalCharges": "Total charges to date",
           "InternetService": "Internet service type", "OnlineSecurity": "Online security",
           "TechSupport": "Tech support", "PaymentMethod": "Payment method",
           "PaperlessBilling": "Paperless billing", "MonthlyCharges": "Monthly charges",
           "MultipleLines": "Multiple lines", "SeniorCitizen": "Senior citizen",
           "StreamingMovies": "Streaming movies"}


def main():
    df = pd.read_csv(ROOT / "data" / "clean" / "telco_churn_scored.csv")
    F = json.loads((ROOT / "data" / "clean" / "findings.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)

    # Customers: one row per customer, with numeric sort columns so bands display in order.
    cust = df.copy()
    cust["TenureBandSort"] = cust["TenureBand"].map({b: i + 1 for i, b in enumerate(TENURE_BANDS)})
    cust["ChargeBandSort"] = cust["MonthlyChargeBand"].map({b: i + 1 for i, b in enumerate(CHARGE_BANDS)})
    cust["RiskBandSort"] = cust["RiskBand"].map({b: i + 1 for i, b in enumerate(RISK_BANDS)})
    cust["RiskScoreBin"] = (cust["RiskScore"] // 10 * 10).clip(upper=90).astype(int)
    cust.to_csv(OUT / "Customers.csv", index=False)

    # Services: one row per internet customer per add-on, for the "service adoption vs churn" chart.
    net = df[df["HasInternet"] == "Yes"]
    long = net.melt(id_vars=["customerID", "Churn"], value_vars=list(ADDONS),
                    var_name="Service", value_name="HasService")
    long["Service"] = long["Service"].map(ADDONS)
    long["HasService"] = long["HasService"].map({"Yes": "Has the service", "No": "Does not have it"})
    long.to_csv(OUT / "Services.csv", index=False)

    # Model results: one row per model.
    pd.DataFrame([
        {"Model": k, "Precision": round(v["precision"], 3), "Recall": round(v["recall"], 3),
         "F1": round(v["f1"], 3), "ROC_AUC": round(v["roc_auc"], 3),
         "UsedForRiskScores": "Yes" if k == F["model"]["chosen"] else "No"}
        for k, v in F["model"]["results"].items()
    ]).to_csv(OUT / "ModelResults.csv", index=False)

    # Churn drivers: relative importance, strongest = 100.
    top = F["drivers_permutation"][:8]
    mx = top[0]["importance"]
    pd.DataFrame([
        {"Driver": DRIVERS.get(d["feature"], d["feature"]), "Rank": i + 1,
         "RelativeImportance": max(1, round(d["importance"] / mx * 100))}
        for i, d in enumerate(top)
    ]).to_csv(OUT / "ChurnDrivers.csv", index=False)

    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name}: {len(pd.read_csv(f)):,} rows")


if __name__ == "__main__":
    main()
