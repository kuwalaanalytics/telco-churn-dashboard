"""Step 3: churn analysis, segments, prediction model and value estimate.

Run from the project root:  python src/analysis.py
Outputs:
  data/clean/telco_churn_scored.csv   (clean data + segment + risk score)
  data/clean/findings.json            (every number quoted in the write-ups)
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.class_weight import compute_sample_weight

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "telco_churn_clean.csv"
OUT = ROOT / "data" / "clean"
SEED = 42

ADDONS = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
          "StreamingTV", "StreamingMovies"]
CAT = ["gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService", "MultipleLines",
       "InternetService", *ADDONS, "Contract", "PaperlessBilling", "PaymentMethod"]
NUM = ["tenure", "MonthlyCharges", "TotalCharges", "NumServices"]
BREAKDOWNS = ["Contract", "TenureBand", "PaymentMethod", "InternetService", "PaperlessBilling",
              "MonthlyChargeBand", "gender", "SeniorCitizen", "Partner", "Dependents", "NumAddOns"]


def rate_table(df, col):
    g = df.groupby(col).agg(customers=("ChurnFlag", "size"), churned=("ChurnFlag", "sum"),
                            churn_rate=("ChurnFlag", "mean"),
                            avg_monthly=("MonthlyCharges", "mean"),
                            monthly_revenue=("MonthlyCharges", "sum"))
    g["revenue_lost"] = df[df.ChurnFlag == 1].groupby(col)["MonthlyCharges"].sum()
    g = g.fillna(0).reset_index().rename(columns={col: "group"})
    g["group"] = g["group"].astype(str)
    return g.round(4).to_dict("records")


def assign_segment(r):
    m2m = r["Contract"] == "Month-to-month"
    if m2m and r["tenure"] <= 12:
        return "New and Uncommitted"
    if m2m and r["InternetService"] == "Fiber optic":
        return "Fibre Flight Risks"
    if m2m:
        return "Settled Month-to-Month"
    if r["MonthlyCharges"] >= 70:
        return "Loyal High-Value"
    return "Committed Essentials"


SEGMENT_RULES = {
    "New and Uncommitted": "Month-to-month contract, 12 months or less with the company",
    "Fibre Flight Risks": "Month-to-month contract, over 12 months tenure, fibre optic internet",
    "Settled Month-to-Month": "Month-to-month contract, over 12 months tenure, DSL or no internet",
    "Loyal High-Value": "One or two year contract, paying $70 or more per month",
    "Committed Essentials": "One or two year contract, paying under $70 per month",
}


def metrics(y, p, thr=0.5):
    pred = (p >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    return {"precision": precision_score(y, pred), "recall": recall_score(y, pred),
            "f1": f1_score(y, pred), "roc_auc": roc_auc_score(y, p),
            "pr_auc": average_precision_score(y, p),
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)}


def make_models():
    def pre(scale):
        return ColumnTransformer([
            ("num", StandardScaler() if scale else "passthrough", NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="if_binary"), CAT)])
    return {
        "Logistic Regression": Pipeline([("pre", pre(True)), ("clf", LogisticRegression(
            class_weight="balanced", max_iter=2000, C=0.5))]),
        "Random Forest": Pipeline([("pre", pre(False)), ("clf", RandomForestClassifier(
            n_estimators=400, min_samples_leaf=8, class_weight="balanced_subsample",
            random_state=SEED, n_jobs=-1))]),
        "Gradient Boosting": Pipeline([("pre", pre(False)), ("clf", GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8,
            random_state=SEED))]),
    }


def oof_scores(model, X, y, cv, weighted):
    """Out-of-fold churn probabilities: each customer is scored by a model that never saw them."""
    oof = np.zeros(len(y))
    for tr, te in cv.split(X, y):
        kw = {"clf__sample_weight": compute_sample_weight("balanced", y.iloc[tr])} if weighted else {}
        model.fit(X.iloc[tr], y.iloc[tr], **kw)
        oof[te] = model.predict_proba(X.iloc[te])[:, 1]
    return oof


def main():
    df = pd.read_csv(CLEAN)
    F = {}

    # ---- Overall -----------------------------------------------------------
    churned = df[df.ChurnFlag == 1]
    F["overall"] = {
        "customers": len(df), "churned": int(df.ChurnFlag.sum()),
        "churn_rate": df.ChurnFlag.mean(), "retention_rate": 1 - df.ChurnFlag.mean(),
        "avg_monthly": df.MonthlyCharges.mean(), "avg_tenure": df.tenure.mean(),
        "total_monthly_revenue": df.MonthlyCharges.sum(),
        "monthly_revenue_lost": churned.MonthlyCharges.sum(),
        "share_revenue_lost": churned.MonthlyCharges.sum() / df.MonthlyCharges.sum(),
        "annualised_revenue_lost": churned.MonthlyCharges.sum() * 12,
        "avg_monthly_churned": churned.MonthlyCharges.mean(),
        "avg_monthly_stayed": df[df.ChurnFlag == 0].MonthlyCharges.mean(),
        "median_tenure_churned": churned.tenure.median(),
        "median_tenure_stayed": df[df.ChurnFlag == 0].tenure.median(),
        # Lifetime value to date: average monthly charge x average months with the company.
        "clv": df.MonthlyCharges.mean() * df.tenure.mean(),
        "avg_total_charges": df.TotalCharges.mean(),
    }

    # ---- Breakdowns --------------------------------------------------------
    F["breakdowns"] = {c: rate_table(df, c) for c in BREAKDOWNS}

    # ---- Services (internet customers only for add-ons) --------------------
    net = df[df.HasInternet == "Yes"]
    svc = []
    for s in ADDONS:
        w, wo = net[net[s] == "Yes"], net[net[s] == "No"]
        svc.append({"service": s, "adoption": len(w) / len(net),
                    "churn_with": w.ChurnFlag.mean(), "churn_without": wo.ChurnFlag.mean(),
                    "customers_with": len(w), "customers_without": len(wo)})
    F["services"] = sorted(svc, key=lambda d: d["churn_with"] - d["churn_without"])
    F["addons_internet"] = rate_table(net, "NumAddOns")
    F["no_addons_internet"] = {
        "customers": int((net.NumAddOns == 0).sum()),
        "churn_no_addons": net[net.NumAddOns == 0].ChurnFlag.mean(),
        "churn_some_addons": net[net.NumAddOns > 0].ChurnFlag.mean()}

    # ---- Segments ----------------------------------------------------------
    df["Segment"] = df.apply(assign_segment, axis=1)
    seg = rate_table(df, "Segment")
    for s in seg:
        sub = df[df.Segment == s["group"]]
        s["rule"] = SEGMENT_RULES[s["group"]]
        s["share_customers"] = len(sub) / len(df)
        s["share_churners"] = sub.ChurnFlag.sum() / df.ChurnFlag.sum()
        s["avg_tenure"] = sub.tenure.mean()
        s["avg_total_charges"] = sub.TotalCharges.mean()
    F["segments"] = sorted(seg, key=lambda d: -d["churn_rate"])

    # ---- Model -------------------------------------------------------------
    X, y = df[CAT + NUM], df.ChurnFlag
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    models, res, oofs = make_models(), {}, {}
    for name, m in models.items():
        # Gradient boosting has no class_weight option, so balance via sample weights.
        weighted = name == "Gradient Boosting"
        oofs[name] = oof_scores(m, X, y, cv, weighted)
        kw = {"clf__sample_weight": compute_sample_weight("balanced", ytr)} if weighted else {}
        m.fit(Xtr, ytr, **kw)
        res[name] = metrics(yte, m.predict_proba(Xte)[:, 1])
        res[name]["cv_roc_auc"] = roc_auc_score(y, oofs[name])
    # Baseline without imbalance handling, to show why it matters.
    base = Pipeline([("pre", models["Logistic Regression"].named_steps["pre"]),
                     ("clf", LogisticRegression(max_iter=2000, C=0.5))]).fit(Xtr, ytr)
    F["model_unweighted_baseline"] = metrics(yte, base.predict_proba(Xte)[:, 1])

    best = max(res, key=lambda k: res[k]["cv_roc_auc"])
    oof = oofs[best]
    F["model"] = {"test_size": len(yte), "test_churners": int(yte.sum()), "chosen": best,
                  "results": res}

    # Drivers: logistic coefficients (direction) and permutation importance (strength).
    lr = models["Logistic Regression"]
    names = lr.named_steps["pre"].get_feature_names_out()
    coefs = pd.Series(lr.named_steps["clf"].coef_[0], index=names)
    coefs.index = coefs.index.str.replace(r"^(num|cat)__", "", regex=True)
    top = coefs.reindex(coefs.abs().sort_values(ascending=False).index).head(14)
    F["drivers_logistic"] = [{"feature": k, "coef": v, "odds_ratio": float(np.exp(v))}
                             for k, v in top.items()]
    pi = permutation_importance(models[best], Xte, yte, scoring="roc_auc", n_repeats=15,
                                random_state=SEED, n_jobs=-1)
    F["drivers_permutation"] = [
        {"feature": f, "importance": i} for f, i in
        sorted(zip(X.columns, pi.importances_mean), key=lambda t: -t[1])[:12]]

    # ---- Risk scores (out-of-fold) -----------------------------------------
    df["RiskScore"] = (oof * 100).round(1)
    df["RiskBand"] = pd.cut(df.RiskScore, [-1, 30, 60, 101], labels=["Low", "Medium", "High"]).astype(str)
    F["risk_bands"] = rate_table(df, "RiskBand")

    # ---- Value of saving the top at-risk customers --------------------------
    ranked = df.sort_values("RiskScore", ascending=False).reset_index(drop=True)
    val = []
    for pct in (0.10, 0.15, 0.20):
        topn = ranked.head(int(round(len(df) * pct)))
        ch = topn[topn.ChurnFlag == 1]
        row = {"top_pct": pct, "customers_contacted": len(topn), "churners_caught": len(ch),
               "hit_rate": len(ch) / len(topn), "share_of_all_churners": len(ch) / df.ChurnFlag.sum(),
               "monthly_revenue_of_caught": ch.MonthlyCharges.sum(),
               "lift_vs_random": (len(ch) / len(topn)) / df.ChurnFlag.mean()}
        for save in (0.2, 0.3, 0.4):
            row[f"saved_monthly_{int(save*100)}"] = ch.MonthlyCharges.sum() * save
            row[f"saved_annual_{int(save*100)}"] = ch.MonthlyCharges.sum() * save * 12
        val.append(row)
    F["value"] = val

    df.to_csv(OUT / "telco_churn_scored.csv", index=False)
    (OUT / "findings.json").write_text(json.dumps(F, indent=2, default=float))
    print("Saved findings.json and telco_churn_scored.csv. Chosen model:", best)


if __name__ == "__main__":
    main()
