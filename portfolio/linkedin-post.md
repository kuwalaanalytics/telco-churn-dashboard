# LinkedIn Content

Live dashboard link to use in every post: https://kuwalaanalytics.github.io/telecom-churn-retention-analysis/

Suggested images: `images/dashboard-screenshot.png` first, then `02-churn-by-contract.png`, `03-churn-by-tenure.png` and `08-value-of-targeting.png`.

---

## Version 1: Short

1 in 4 customers left in a single month. They took 30% of monthly revenue with them.

I built a churn analysis and interactive dashboard to show how a telecom or subscription business can see this coming.

Three things stood out:

1. Month-to-month customers leave at 42.7%. On two year contracts it is 2.8%.
2. More than half of customers in their first 6 months leave.
3. A prediction model found 51% of all leavers by looking at only the riskiest 20% of customers.

This uses the public IBM Telco sample dataset to demonstrate the approach. It is not client data.

Explore the live dashboard: https://kuwalaanalytics.github.io/telecom-churn-retention-analysis/

#CustomerChurn #DataAnalytics #Telecom #BusinessIntelligence #Malawi

---

## Version 2: Storytelling

Most businesses find out a customer is unhappy on the day they leave.

By then it is too late. The number is ported, the subscription is cancelled, and the monthly revenue is gone.

I wanted to show what it looks like when you can see it coming instead. So I took the public IBM Telco sample dataset (7,043 customers) and treated it like a real client brief: who is leaving, why, and who should we call this week?

The data told a clear story.

The customers most likely to leave were new, on month-to-month plans, and had no support or security add-ons. More than half of customers in their first 6 months left. Among customers who had stayed over 4 years, fewer than 1 in 10 did.

And the leavers were not the small accounts. They paid $74 a month on average, against $61 for those who stayed.

Then I built a model to score every customer's risk. The riskiest 20% of the list contained 51% of everyone who left. That is the difference between a call centre phoning customers at random and one that knows where to start.

The result is one dashboard an owner can open on a laptop or phone, filter by contract or payment method, and get a ranked list of customers to call.

To be clear, this is a demonstration on public sample data, not a client project. The approach is the same one I would bring to your customer data.

See it live: https://kuwalaanalytics.github.io/telecom-churn-retention-analysis/

If your business loses customers each month and you are not sure why, I would be glad to talk.

#CustomerRetention #CustomerChurn #DataAnalytics #MachineLearning #Malawi #KuwalaAnalytics

---

## Version 3: Results-focused

Customer churn analysis: the numbers.

Dataset: public IBM Telco sample, 7,043 customers (a demonstration, not client data).

What I found:

- Churn rate: 26.5%
- Monthly revenue lost: $139,131, which is 30.5% of monthly billing
- Month-to-month contracts: 42.7% churn. Two year contracts: 2.8%
- First 6 months: 52.9% churn. After 4 years: 9.5%
- Electronic check payers: 45.3% churn. Automatic payers: 15% to 17%
- With online security: 14.6% churn. Without: 41.8%

What I built:

- A churn prediction model with 78% recall and 0.84 ROC-AUC, tested on customers it had never seen
- 5 named customer segments. Two of them hold 46% of customers and 83% of leavers
- A ranked at-risk customer list
- An interactive dashboard with filters, 7 KPIs and 6 retention recommendations

What it could be worth:

The riskiest 20% of customers contained 51% of all leavers. If a retention offer kept 30% of those, that is about $270,000 a year in protected revenue on this dataset. The 30% is an assumption that a real project would test.

Live dashboard: https://kuwalaanalytics.github.io/telecom-churn-retention-analysis/

Tools: Python, pandas, scikit-learn, Plotly, Chart.js.

#DataAnalytics #CustomerChurn #PredictiveAnalytics #Python #BusinessIntelligence #KuwalaAnalytics

---

## Featured section description

**Title:** Telecom Customer Churn and Retention Analysis: Dashboard and Prediction Model

**Description:**
An end-to-end churn analysis showing who is leaving a telecom business, how much revenue goes with them, and which customers to call first. Includes an interactive dashboard with filters and KPIs, five customer segments, a prediction model that finds 51% of leavers in the riskiest 20% of customers, and six retention recommendations. Built with Python, scikit-learn and Chart.js on the public IBM Telco sample dataset to demonstrate the approach.
