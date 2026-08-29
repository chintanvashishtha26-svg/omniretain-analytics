# OmniRetain | Superstore Customer Segmentation & A/B Experimentation Engine

An end-to-end data analytics platform processing real retail transactions into actionable RFM cohorts and evaluating retention marketing strategies using statistical hypothesis testing.

## 📌 Project Overview
- **Data Engineering:** Ingested and cleaned 9,900+ real retail records from the Superstore dataset.
- **RFM Segmentation Pipeline:** Transformed raw orders into Recency, Frequency, and Monetary quintiles using advanced SQL CTEs and window functions.
- **Interactive BI Dashboard:** Built a responsive decision-support application in Streamlit with Plotly visualizations.
- **Hypothesis Testing:** Integrated a dynamic A/B test simulation tool running two-tailed Chi-Square ($\chi^2$) tests to evaluate conversion uplifts on at-risk accounts.

## 🛠️ Tech Stack
- **Languages & Libraries:** Python (Pandas, Scipy, NumPy, Plotly)
- **Database / Transformation:** SQL (PostgreSQL dialect)
- **Framework & Deployment:** Streamlit, Git, Streamlit Cloud

## 🚀 Local Installation
```bash
git clone https://github.com/Chintan-vashishtha/omniretain-analytics.git
cd omniretain-analytics
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py