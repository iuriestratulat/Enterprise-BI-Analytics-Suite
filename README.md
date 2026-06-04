# Enterprise BI Analytics & Production Data Suite

An enterprise-grade, cloud-native Business Intelligence platform engineered to process, analyze, and visualize multi-million euro operations. This system bypasses traditional local file storage bottlenecks by utilizing a fully secure, remote architecture powered by **Google Cloud Platform (GCP)** and optimized memory data processing via **Polars**.

🚀 **Live Application:** [Enterprise Business Intelligence Analytics Suite](https://stratulat-bi-suite.streamlit.app/)

---

## 📈 Executive Business Insights & Frameworks

The suite transforms raw production and sales logs into structured financial and operational frameworks across multiple integrated modules:

* **I. Time Series Analysis & Forecasting:** Incorporates advanced statistical models, including rolling metrics and optimized Moving Averages, to identify cyclical revenue trends and seasonal demand patterns (€3.58M total revenue analyzed).
* **II. Campaign & Source Effectiveness:** ROI and marginal utility evaluation of marketing spend across various acquisition channels.
* **III. Sales Team Performance:** Granular tracking of sales rep throughput, analyzing call-to-deal conversion rates, communication velocity, and individual revenue attribution.
* **IV. Products and Payments Analysis:** Comprehensive audit of payment gateways, transaction success metrics, and product-specific revenue generation.
* **V. Advanced Geographic Mapping:** Dynamic multi-layered density visualization mapping client distributions and sales performance across pan-European jurisdictions and deep-dive regional analysis of German states (`DE_regions`).
* **VI. Unit Economics & Product Strategy:** Deep-dive calculation of core enterprise unit metrics including Customer Acquisition Cost (CAC), Lifetime Value (LTV), Contribution Margins, and A/B Testing Parameter Configurations.

---

## 🏗️ Technical Architecture & Cloud Infrastructure

This repository demonstrates modern Data Engineering and BI Architecture patterns designed for secure, scalable production environments.

### Data Flow Architecture
1. **Source Layer:** Raw transaction and call center logs are compressed into highly optimized Apache Parquet columnar files to minimize cold-storage footprint.
2. **Cloud Infrastructure Layer:** Data is stored in an isolated, private **Google Cloud Storage (GCS)** bucket situated in the `europe-west1` (Belgium) data center region. Public access is strictly prohibited by infrastructure-level firewall rules.
3. **Secure Authentication Layer:** Application access is governed by the principle of *Least Privilege*. A dedicated GCP Service Account (`Storage Object Viewer` role) authenticates requests via encrypted asymmetric JSON cryptographic keys managed through Streamlit Secrets.
4. **Compute & In-Memory Layer:** Instead of legacy Pandas processing, the execution engine uses **Polars**, leveraging multi-threaded SIMD architecture to read cloud byte-streams straight into memory instantly.

## 📂 Project Structure

```text
Enterprise-BI-Suite/
├── bi_modules/                             # Core analytical logic & data processing
│   ├── analytics_time_series.py            # Sales velocity & seasonal trend analysis
│   ├── analytics_campaigns.py              # Multi-channel marketing efficiency & ROAS tracking
│   ├── analytics_sales_team.py             # CRM pipelines, stage transitions & SLA monitoring
│   ├── analytics_products.py               # Multi-currency subscriptions & transaction risks
│   ├── analytics_geo.py                    # GeoJSON customer density & regional demand mapping
│   └── ue_analysis.py                      # Math engine: Contribution Margins & sensitivity metrics
│
├── pages/                                  # Streamlit multi-page interface UI
│   ├── 1_Analytics_Time_Series.py          # UI: Sales velocity & historical trends dashboard
│   ├── 2_Campaign_Effectiveness.py         # UI: Marketing performance & ROAS allocation
│   ├── 3_Sales_Team_Performance.py         # UI: CRM pipeline speed & SLA metrics dashboard
│   ├── 4_Products_and_Payments.py          # UI: Subscription cash flow & collections risk
│   ├── 5_Geographic_Analysis.py            # UI: Interactive GeoJSON demand & density maps
│   └── 6_Unit_Economics.py                 # UI: Enterprise unit economics entry point
│
├── ue_modules/                             # Sub-modules for Unit Economics engine
│   ├── ue_utils.py                         # Config for global Unit Economics summary cards
│   ├── vi1_dashboard.py                    # Unit Economics Breakdown per Product
│   ├── vi2_dashboard.py                    # Sensitivity Analysis: Growth Levers vs. CM (%)
│   ├── vi3_dashboard.py                    # Interactive Unit Economics Metrics Tree Hierarchy
│   ├── vi4_dashboard.py                    # A/B Testing analytical engine
│   └── vi5_dashboard.py                    # SMART Objectives & HADI Optimization framework
│
├── utilities/                              # Data pipeline & helper resources
│   ├── Countries.py                        # Country-to-city mapping dictionaries
│   ├── DE_regions.py                       # German states (Bundesländer) regional dictionary
│   ├── data_loader.py                      # Optimized Parquet data loading for Streamlit
│   ├── metrics_tree.png                    # Metrics Tree architecture diagram for UE module
│   └── pipeline_of_project.py              # ETL pipeline: Raw CSV data cleaning to Parquet
│
├── app_streamlit.py                        # Main application entry point for launching the Streamlit dashboard
├── packages.txt                            # Linux system dependencies for Streamlit (GDAL/GIS)
└── requirements.txt                        # Python library dependencies
```
