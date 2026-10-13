"""Step 4: build the single-file interactive dashboard.

Run from the project root:  python src/build_dashboard.py
Reads data/clean/telco_churn_scored.csv and data/clean/findings.json, then writes
dashboard/index.html with the data, Chart.js and the logo embedded so it opens offline.
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
import base64
import json

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
TEMPLATE = SRC / "dashboard_template.html"
CHARTJS = SRC / "vendor" / "chart.umd.min.js"
LOGO = ROOT / "assets" / "kuwala-logo.jpg"
OUT = ROOT / "dashboard" / "index.html"

CONTRACT = ["Month-to-month", "One year", "Two year"]
INTERNET = ["DSL", "Fiber optic", "No"]
PAYMENT = ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
TENURE_BANDS = ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49-72 months"]
CHARGE_BANDS = ["Under $30", "$30-49", "$50-69", "$70-89", "$90+"]
ADDONS = {"OnlineSecurity": "Online security", "TechSupport": "Tech support",
          "OnlineBackup": "Online backup", "DeviceProtection": "Device protection",
          "StreamingTV": "Streaming TV", "StreamingMovies": "Streaming movies"}
DEMO_LABELS = ["Senior citizen", "Not senior", "No partner", "Has partner",
               "No dependents", "Has dependents", "Female", "Male"]
DRIVER_TEXT = {
    "Contract": ("Contract type", "Month-to-month customers leave far more often than those on 1 or 2 year contracts."),
    "tenure": ("Tenure", "Newer customers are much more likely to leave. Risk drops steadily with time."),
    "TotalCharges": ("Total charges to date", "Reflects how long and how much a customer has paid so far."),
    "InternetService": ("Internet service type", "Fibre optic customers churn more than DSL customers."),
    "OnlineSecurity": ("Online security", "Customers with online security leave less often."),
    "TechSupport": ("Tech support", "Customers with tech support leave less often."),
    "PaymentMethod": ("Payment method", "Electronic check payers leave more often than automatic payers."),
    "PaperlessBilling": ("Paperless billing", "Paperless billing customers churn more often."),
    "MonthlyCharges": ("Monthly charges", "Higher bills go with higher churn."),
    "MultipleLines": ("Multiple lines", "A small effect once other factors are known."),
    "SeniorCitizen": ("Senior citizen", "Seniors churn more often."),
    "StreamingMovies": ("Streaming movies", "A small effect once other factors are known."),
    "StreamingTV": ("Streaming TV", "A small effect once other factors are known."),
    "Dependents": ("Dependents", "Customers with dependents leave less often."),
    "Partner": ("Partner", "Customers with a partner leave less often."),
    "OnlineBackup": ("Online backup", "Customers with online backup leave less often."),
    "DeviceProtection": ("Device protection", "Customers with device protection leave less often."),
    "NumServices": ("Number of services", "Customers with more services leave less often."),
    "PhoneService": ("Phone service", "A small effect once other factors are known."),
    "gender": ("Gender", "No meaningful effect."),
}


def logo_data_uri() -> str:
    """Crop the bulb icon out of the full logo and embed it as a small PNG."""
    im = Image.open(LOGO).convert("RGB").crop((440, 20, 1430, 1140))
    im.thumbnail((160, 160))
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def money(v):
    return f"${v:,.0f}"


def build_payload(df: pd.DataFrame, F: dict) -> dict:
    addon_cols = list(ADDONS)
    bits = sum((df[c] == "Yes").astype(int) * (1 << i) for i, c in enumerate(addon_cols))
    rows = [
        [r.customerID, CONTRACT.index(r.Contract), INTERNET.index(r.InternetService),
         PAYMENT.index(r.PaymentMethod), TENURE_BANDS.index(r.TenureBand),
         int(r.SeniorCitizen == "Yes"), int(r.tenure), float(r.MonthlyCharges), int(r.ChurnFlag),
         float(r.RiskScore), int(r.gender == "Male"), int(r.Partner == "Yes"),
         int(r.Dependents == "Yes"), int(b)]
        for r, b in zip(df.itertuples(), bits)
    ]
    top = F["drivers_permutation"][:8]
    mx = top[0]["importance"]
    drivers = [{"label": DRIVER_TEXT[d["feature"]][0], "note": DRIVER_TEXT[d["feature"]][1],
                "score": max(1, round(d["importance"] / mx * 100))} for d in top]
    return {"rows": rows,
            "dims": {"contract": CONTRACT, "internet": INTERNET, "payment": PAYMENT,
                     "tenureBand": TENURE_BANDS, "chargeBand": CHARGE_BANDS},
            "addons": list(ADDONS.values()), "demoLabels": DEMO_LABELS, "drivers": drivers}


def recommendations(F: dict) -> str:
    b = {c: {g["group"]: g for g in gs} for c, gs in F["breakdowns"].items()}
    svc = {s["service"]: s for s in F["services"]}
    o, v20 = F["overall"], F["value"][-1]
    recs = [
        ("1. Win the first six months",
         f"{pct(b['TenureBand']['0-6 months']['churn_rate'])} of customers in their first 6 months leave, against "
         f"{pct(b['TenureBand']['49-72 months']['churn_rate'])} after 4 years. Add a welcome call, a 30 day check-in "
         "and a 90 day review for every new customer."),
        ("2. Move month-to-month customers onto contracts",
         f"Month-to-month churn is {pct(b['Contract']['Month-to-month']['churn_rate'])}, versus "
         f"{pct(b['Contract']['One year']['churn_rate'])} on one year and {pct(b['Contract']['Two year']['churn_rate'])} "
         "on two year contracts. Offer a discount or free add-on for committing to 12 months."),
        ("3. Bundle online security and tech support",
         f"Internet customers with online security churn at {pct(svc['OnlineSecurity']['churn_with'])} versus "
         f"{pct(svc['OnlineSecurity']['churn_without'])} without; tech support shows {pct(svc['TechSupport']['churn_with'])} "
         f"versus {pct(svc['TechSupport']['churn_without'])}. Trial these free for 3 months with customers who have no add-ons."),
        ("4. Shift electronic check payers to automatic payment",
         f"Electronic check payers churn at {pct(b['PaymentMethod']['Electronic check']['churn_rate'])}, about three times "
         f"the {pct(b['PaymentMethod']['Credit card (automatic)']['churn_rate'])} to "
         f"{pct(b['PaymentMethod']['Bank transfer (automatic)']['churn_rate'])} seen on automatic payments. "
         "Give a small bill credit for switching."),
        ("5. Review the fibre optic experience and price",
         f"Fibre customers churn at {pct(b['InternetService']['Fiber optic']['churn_rate'])} and account for "
         f"{money(b['InternetService']['Fiber optic']['revenue_lost'])} of the {money(o['monthly_revenue_lost'])} lost each "
         "month. Survey leavers and check price and service quality against competitors."),
        ("6. Call the highest-risk customers every week",
         f"The top 20% of customers by risk score contained {pct(v20['share_of_all_churners'], 0)} of all leavers in a "
         f"back-test. If a retention offer kept 30% of them, that is about {money(v20['saved_annual_30'])} a year "
         "(the 30% save rate is an assumption, not a measured result)."),
    ]
    return "".join(f'<div class="rec"><h3>{t}</h3><p>{p}</p></div>' for t, p in recs)


def main():
    df = pd.read_csv(ROOT / "data" / "clean" / "telco_churn_scored.csv")
    F = json.loads((ROOT / "data" / "clean" / "findings.json").read_text())
    name = F["model"]["chosen"]
    m = F["model"]["results"][name]
    v10, v20 = F["value"][0], F["value"][-1]
    model_plain = (
        f"In plain language: of every 100 customers who really left, the model flagged {m['recall'] * 100:.0f} in advance "
        f"(recall). Of every 100 customers it flagged, {m['precision'] * 100:.0f} really left (precision). "
        "Classes were balanced during training so the model does not ignore the smaller group of leavers. "
        "A simpler logistic regression scored almost the same, so the result does not depend on one technique.")
    value_plain = (
        f"Why this list matters: in a back-test, the riskiest 10% of customers contained {pct(v10['share_of_all_churners'], 0)} "
        f"of all leavers and the riskiest 20% contained {pct(v20['share_of_all_churners'], 0)}. "
        f"Random calling would find {pct(F['overall']['churn_rate'], 0)}; this list finds {pct(v20['hit_rate'], 0)} to "
        f"{pct(v10['hit_rate'], 0)}.")
    logo = logo_data_uri()
    now = datetime.now()
    refreshed = f"{now:%b} {now.day}, {now:%Y} {now.hour % 12 or 12}:{now:%M %p}"
    html = TEMPLATE.read_text()
    for key, val in {
        "__LOGO__": logo, "__REFRESHED__": refreshed, "__MODEL_NAME__": name,
        "__TEST_N__": f"{F['model']['test_size']:,}", "__RECALL__": pct(m["recall"], 0),
        "__PRECISION__": pct(m["precision"], 0), "__F1__": f"{m['f1']:.2f}", "__AUC__": f"{m['roc_auc']:.2f}",
        "__MODEL_PLAIN__": model_plain, "__VALUE_PLAIN__": value_plain, "__RECS__": recommendations(F),
        "__DATA__": json.dumps(build_payload(df, F), separators=(",", ":")),
        "__CHARTJS__": CHARTJS.read_text(),
    }.items():
        html = html.replace(key, val)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    # Root page so the GitHub Pages site address opens the dashboard directly.
    (ROOT / "index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><title>Telecom Customer Churn and Retention Analysis | Kuwala Analytics</title>'
        '<meta http-equiv="refresh" content="0; url=dashboard/"><a href="dashboard/">Open the dashboard</a>\n')
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
