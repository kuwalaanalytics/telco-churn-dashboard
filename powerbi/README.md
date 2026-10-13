# Power BI Pack

Everything needed to rebuild the churn dashboard in Power BI Desktop on a Windows machine. Allow about 1 to 2 hours for the first build.

> This pack was prepared without access to Power BI Desktop, so it has not been test-built. The data files are checked; the DAX measures and theme follow standard patterns but may need small fixes when you first load them.

## What is in this folder

| File | Purpose |
|---|---|
| `data/Customers.csv` | One row per customer (7,043 rows) with segment, risk score, risk band and sort columns |
| `data/Services.csv` | One row per internet customer per add-on service, for the service chart |
| `data/ModelResults.csv` | Precision, recall, F1 and ROC-AUC for the three models |
| `data/ChurnDrivers.csv` | Top 8 churn drivers with relative importance |
| `measures.dax` | All measures, ready to paste in |
| `kuwala-theme.json` | Kuwala Analytics colours and fonts |

The logo is at `../assets/kuwala-logo.jpg`.

## Step 1: Load the data

1. Open Power BI Desktop. Choose **Get data > Text/CSV** and load each of the four files in `data/`.
2. In the preview, click **Load** (no transformation is needed).
3. Check the data types in **Table view**:
   - `Customers[MonthlyCharges]`, `Customers[TotalCharges]`, `Customers[RiskScore]`: Decimal number
   - `Customers[tenure]`, `Customers[NumServices]`, `Customers[NumAddOns]`, `Customers[ChurnFlag]` and the three `...Sort` columns: Whole number
   - `Customers[RiskScoreBin]`: Whole number

## Step 2: Set up the model

1. Open **Model view**. Create one relationship: `Customers[customerID]` (one) to `Services[customerID]` (many), single direction. This lets the slicers filter the service chart.
2. Leave `ModelResults` and `ChurnDrivers` unconnected. They do not change with filters.
3. Set the sort order so bands appear in the right order. Select the column, then **Column tools > Sort by column**:
   - `TenureBand` sorted by `TenureBandSort`
   - `MonthlyChargeBand` sorted by `ChargeBandSort`
   - `RiskBand` sorted by `RiskBandSort`
   - `ChurnDrivers[Driver]` sorted by `Rank`

## Step 3: Add the measures

Open `measures.dax` in Notepad. For each measure, right-click the table named in the file, choose **New measure**, paste the measure and set the format noted in its comment.

## Step 4: Apply the theme

**View > Themes > Browse for themes**, then pick `kuwala-theme.json`. Set the page size to 16:9 (**Format page > Canvas settings**).

## Step 5: Build the pages

### Page 1: Overview

| Area | Visual | Fields |
|---|---|---|
| Top left | Image | `kuwala-logo.jpg` |
| Top | Text box | Title: "Telecom Customer Churn and Retention Analysis" |
| Filter row | 5 slicers (dropdown style) | `Contract`, `InternetService`, `PaymentMethod`, `TenureBand`, `SeniorCitizen` |
| KPI row | 7 cards | `Total Customers`, `Churn Rate`, `Retention Rate`, `Avg Monthly Charges`, `Avg Tenure (Months)`, `Monthly Revenue at Risk`, `Customer Lifetime Value` |
| Row 1 | Clustered column chart | Axis: `Contract`. Values: `Churn Rate` |
| Row 1 | Line chart | Axis: `TenureBand`. Values: `Churn Rate` |
| Row 1 | Line and clustered column chart | Axis: `MonthlyChargeBand`. Column: `Total Customers`. Line: `Churn Rate` |
| Row 2 | Clustered bar chart | Axis: `Services[Service]`. Legend: `Services[HasService]`. Values: `Service Churn Rate` |
| Row 2 | Stacked bar chart | Axis: `PaymentMethod`. Legend: `Churn`. Values: `Total Customers` |
| Row 2 | Clustered bar charts (4 small) | One each for `SeniorCitizen`, `Partner`, `Dependents`, `gender`. Values: `Churn Rate` |

Turn on data labels for every chart. For the stacked bar, set the colours so `No` (stayed) is navy and `Yes` (churned) is orange.

### Page 2: At-risk customers and model

| Area | Visual | Fields |
|---|---|---|
| Top | 3 cards | `Current Customers`, `High Risk Customers`, `High Risk Monthly Revenue` |
| Left | Table | `customerID`, `RiskScore`, `RiskBand`, `Contract`, `tenure`, `MonthlyCharges`, `InternetService`, `PaymentMethod`. Add a visual-level filter: `Churn` is `No`. Sort by `RiskScore` descending |
| Right top | Table | `ModelResults`: all columns |
| Right middle | Clustered bar chart | Axis: `ChurnDrivers[Driver]`. Values: `RelativeImportance` |
| Right bottom | Stacked column chart | Axis: `RiskScoreBin`. Legend: `Churn`. Values: `Total Customers` |

For the table, add **Conditional formatting > Data bars** on `RiskScore` (orange), and set `RiskScore` and `tenure` to "Don't summarize". Copy the five slicers from page 1 and use **View > Sync slicers** so filters carry across pages.

### Page 3: Segments and recommendations

| Area | Visual | Fields |
|---|---|---|
| Top | Clustered bar chart | Axis: `Segment`. Values: `Churn Rate` |
| Middle | Table | `Segment`, `Total Customers`, `Churn Rate`, `Avg Monthly Charges`, `Monthly Revenue at Risk` |
| Bottom | Text boxes | The six recommendations from `../portfolio/case-study.md` |

Add a text box on every page: "Public IBM Telco sample dataset, used to demonstrate the approach. Not client data."

## Step 6: Check the numbers

With no filters applied, the cards should read:

| Measure | Expected |
|---|---|
| Total Customers | 7,043 |
| Churn Rate | 26.5% |
| Retention Rate | 73.5% |
| Avg Monthly Charges | $64.76 |
| Avg Tenure (Months) | 32.4 |
| Monthly Revenue at Risk | $139,131 |
| Customer Lifetime Value | $2,096 |
| Current Customers | 5,174 |
| High Risk Customers | 979 |

If these match the HTML dashboard, the model is set up correctly.

## Step 7: Share it

- **For a portfolio:** save the `.pbix` file and take screenshots of each page. This needs no licence.
- **For a public link:** sign in with a work or school account, publish to the Power BI service, then use **File > Embed report > Publish to web**. A personal email address (such as Gmail) cannot sign in to the Power BI service.

## Refreshing the data

Re-run `python src/make_powerbi_pack.py` from the project root to regenerate the CSV files, then click **Refresh** in Power BI Desktop.
