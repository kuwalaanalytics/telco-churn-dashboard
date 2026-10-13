"""Step 5: export branded chart images for social media (1080 x 1080, saved at 2x).

Run from the project root:  python src/make_charts.py
Reads data/clean/findings.json and writes PNG files to portfolio/images/.
"""
from pathlib import Path
import base64
import json

import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "portfolio" / "images"
F = json.loads((ROOT / "data" / "clean" / "findings.json").read_text())
LOGO = "data:image/jpeg;base64," + base64.b64encode((ROOT / "assets" / "kuwala-logo.jpg").read_bytes()).decode()

NAVY, ORANGE, PALE, INK, MUTED, GRID = "#2F4B8F", "#E8590C", "#C9D4EA", "#141C33", "#6B7588", "#E3E7EF"
FONT = "Inter, Segoe UI, Helvetica Neue, Arial, sans-serif"
FOOTER = "Public IBM Telco sample dataset (7,043 customers), used to demonstrate the approach. Not client data."

B = {c: {g["group"]: g for g in gs} for c, gs in F["breakdowns"].items()}
O = F["overall"]


def base(title: str, subtitle: str, l: int = 90, r: int = 80) -> go.Figure:
    """Blank branded canvas. Footer and logo are pinned to fixed pixel positions for any margin."""
    fig = go.Figure()
    plot_w = 1080 - l - r
    fig.update_layout(
        width=1080, height=1080, paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family=FONT, size=24, color=INK),
        margin=dict(l=l, r=r, t=250, b=190), showlegend=False, bargap=0.38,
        title=dict(text=f"<b>{title}</b><br><span style='font-size:25px;color:{MUTED}'>{subtitle}</span>",
                   x=0.06, xanchor="left", y=0.93, yanchor="top", font=dict(size=42, color=INK)),
    )
    fig.add_layout_image(dict(source=LOGO, xref="paper", yref="paper", x=(1050 - l) / plot_w, y=-0.115,
                              sizex=120 / plot_w, sizey=0.13, xanchor="right", yanchor="top"))
    fig.add_annotation(text=FOOTER, xref="paper", yref="paper", x=(50 - l) / plot_w, y=-0.2, xanchor="left",
                       yanchor="top", showarrow=False, font=dict(size=17, color=MUTED), align="left")
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(size=24))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(size=20, color=MUTED), ticksuffix="%")
    return fig


def vbar(fig, labels, values, highlight=0, fmt="{:.1f}%"):
    colors = [ORANGE if i == highlight else NAVY for i in range(len(labels))]
    fig.add_bar(x=labels, y=values, marker=dict(color=colors, cornerradius=8),
                text=[fmt.format(v) for v in values], textposition="outside",
                textfont=dict(size=34, color=INK), cliponaxis=False)
    fig.update_yaxes(range=[0, max(values) * 1.18])
    return fig


def hbar(fig, labels, values, colors, fmt="{:.1f}%"):
    fig.add_bar(y=labels, x=values, orientation="h", marker=dict(color=colors, cornerradius=8),
                text=[fmt.format(v) for v in values], textposition="outside",
                textfont=dict(size=28, color=INK), cliponaxis=False)
    fig.update_xaxes(range=[0, max(values) * 1.2], showgrid=True, gridcolor=GRID, ticksuffix="%",
                     tickfont=dict(size=20, color=MUTED))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticklabelstandoff=14, ticksuffix="", automargin=False, tickfont=dict(size=24, color=INK))
    return fig


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.write_image(OUT / name, scale=2)
    print("saved", name)


def chart_overview():
    fig = base("1 in 4 customers left last month", "Overall churn and the revenue that went with it")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    for y, big, small, color in [
        (0.78, f"{O['churn_rate'] * 100:.1f}%", f"churn rate ({O['churned']:,} of {O['customers']:,} customers)", ORANGE),
        (0.44, f"${O['monthly_revenue_lost']:,.0f}", f"monthly revenue lost, {O['share_revenue_lost'] * 100:.1f}% of all monthly billing", NAVY),
        (0.10, f"${O['avg_monthly_churned']:.0f} vs ${O['avg_monthly_stayed']:.0f}", "average monthly bill: customers who left vs customers who stayed", INK),
    ]:
        # "&#36;" instead of "$" so paired dollar signs are not read as LaTeX maths.
        fig.add_annotation(text=f"<b>{big}</b>".replace("$", "&#36;"), xref="paper", yref="paper", x=0, y=y,
                           xanchor="left", yanchor="bottom", showarrow=False, font=dict(size=100, color=color))
        fig.add_annotation(text=small, xref="paper", yref="paper", x=0, y=y, xanchor="left", yanchor="top",
                           showarrow=False, font=dict(size=27, color=MUTED))
    save(fig, "01-overall-churn.png")


def chart_contract():
    labels = ["Month-to-month", "One year", "Two year"]
    fig = base("Contracts keep customers", "Churn rate by contract type")
    save(vbar(fig, labels, [B["Contract"][l]["churn_rate"] * 100 for l in labels]), "02-churn-by-contract.png")


def chart_tenure():
    bands = ["0-6 months", "7-12 months", "13-24 months", "25-48 months", "49-72 months"]
    fig = base("The first 6 months decide it", "Churn rate by time with the company (months)")
    save(vbar(fig, [b.replace(" months", "") for b in bands],
              [B["TenureBand"][b]["churn_rate"] * 100 for b in bands]), "03-churn-by-tenure.png")


def chart_payment():
    labels = ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
    vals = [B["PaymentMethod"][l]["churn_rate"] * 100 for l in labels]
    fig = base("How customers pay predicts who leaves", "Churn rate by payment method")
    short = [l.replace(" (automatic)", "<br>(automatic)").replace(" check", "<br>check") for l in labels]
    save(vbar(fig, short, vals), "04-churn-by-payment-method.png")


def chart_services():
    names = {"OnlineSecurity": "Online security", "TechSupport": "Tech support",
             "OnlineBackup": "Online backup", "DeviceProtection": "Device protection",
             "StreamingTV": "Streaming TV", "StreamingMovies": "Streaming movies"}
    svc = F["services"]
    fig = base("Support add-ons cut churn sharply", "Churn rate among internet customers, with and without each service", l=250)
    labels = [names[s["service"]] for s in svc]
    for key, name, color in [("churn_with", "Has the service", NAVY), ("churn_without", "Does not have it", ORANGE)]:
        vals = [s[key] * 100 for s in svc]
        fig.add_bar(y=labels, x=vals, name=name, orientation="h", marker=dict(color=color, cornerradius=6),
                    text=[f"{v:.0f}%" for v in vals], textposition="outside", textfont=dict(size=22, color=INK),
                    cliponaxis=False)
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08, showlegend=True,
                      legend=dict(orientation="h", x=0, y=1.07, font=dict(size=22), traceorder="normal"))
    fig.update_xaxes(range=[0, 50], showgrid=True, gridcolor=GRID, ticksuffix="%", tickfont=dict(size=20, color=MUTED))
    fig.update_yaxes(autorange="reversed", showgrid=False, ticklabelstandoff=14, ticksuffix="", automargin=False, tickfont=dict(size=23, color=INK))
    save(fig, "05-services-vs-churn.png")


def chart_segments():
    seg = F["segments"]
    fig = base("Five customer segments, very different risk", "Churn rate by segment, with size and average monthly bill", l=330, r=110)
    labels = [f"<b>{s['group']}</b><br><span style='font-size:18px;color:{MUTED}'>"
              f"{s['customers']:,} customers, &#36;{s['avg_monthly']:.0f}/month</span>" for s in seg]
    colors = [ORANGE if s["churn_rate"] > O["churn_rate"] else NAVY for s in seg]
    hbar(fig, labels, [s["churn_rate"] * 100 for s in seg], colors)
    fig.update_layout(bargap=0.42)
    save(fig, "06-customer-segments.png")


def chart_drivers():
    names = {"Contract": "Contract type", "tenure": "Tenure", "TotalCharges": "Total charges to date",
             "InternetService": "Internet service type", "OnlineSecurity": "Online security",
             "TechSupport": "Tech support", "PaymentMethod": "Payment method",
             "PaperlessBilling": "Paperless billing", "MonthlyCharges": "Monthly charges",
             "MultipleLines": "Multiple lines"}
    top = F["drivers_permutation"][:8]
    mx = top[0]["importance"]
    vals = [max(1, round(d["importance"] / mx * 100)) for d in top]
    fig = base("What drives churn the most", "Top churn drivers from the prediction model (strongest = 100)", l=290)
    hbar(fig, [names.get(d["feature"], d["feature"]) for d in top], vals, [NAVY] * len(top), fmt="{}")
    fig.update_xaxes(ticksuffix="", range=[0, 115])
    save(fig, "07-top-churn-drivers.png")


def chart_value():
    val = F["value"]
    fig = base("Call the right 20%, reach half the leavers",
               "Share of all leavers found among the highest-risk customers (back-test)")
    labels = [f"Top {v['top_pct'] * 100:.0f}%<br>by risk score" for v in val]
    vbar(fig, labels, [v["share_of_all_churners"] * 100 for v in val], highlight=2, fmt="{:.0f}%")
    v20 = val[-1]
    fig.add_annotation(
        text=(f"If a retention offer kept 30% of the leavers in the top 20%,<br>that is about "
              f"<b>&#36;{v20['saved_annual_30']:,.0f} a year</b> (30% is an assumption)."),
        xref="paper", yref="paper", x=0, y=1.0, xanchor="left", yanchor="top", showarrow=False, align="left",
        font=dict(size=24, color=INK), bgcolor="#FFF6D6", borderpad=12)
    fig.update_yaxes(range=[0, 78])
    save(fig, "08-value-of-targeting.png")


if __name__ == "__main__":
    for fn in (chart_overview, chart_contract, chart_tenure, chart_payment, chart_services,
               chart_segments, chart_drivers, chart_value):
        fn()
