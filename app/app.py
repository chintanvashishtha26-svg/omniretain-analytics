import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import chi2_contingency
import os

st.set_page_config(page_title="OmniRetain | Superstore Analytics", layout="wide")

st.title("⚡ OmniRetain - Customer Intelligence & Retention Engine")
st.caption("Retail Analytics Pipeline & Retention Experimentation Platform")

# Load and process Superstore CSV
@st.cache_data
def load_and_process_superstore():
    file_path = 'data/Sample - Superstore.csv'
    
    if not os.path.exists(file_path):
        st.error(f"Dataset not found at {file_path}. Please verify the file location.")
        return pd.DataFrame()
    
    # Read with fallback encoding
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
    
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    clean_df = df[df['Sales'] > 0].copy()
    
    # RFM Aggregation
    snapshot_date = clean_df['Order Date'].max() + pd.Timedelta(days=1)
    
    rfm = clean_df.groupby('Customer ID').agg(
        recency=('Order Date', lambda x: (snapshot_date - x.max()).days),
        frequency=('Order ID', 'nunique'),
        monetary=('Sales', 'sum')
    ).reset_index()
    
    # 5-Quintile Scoring
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    def tag_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r >= 3 and f < 3:
            return 'Promising'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f < 3:
            return 'Lost'
        return 'Regular'

    rfm['segment'] = rfm.apply(tag_segment, axis=1)
    return rfm

df_rfm = load_and_process_superstore()

if not df_rfm.empty:
    # Sidebar Filters
    st.sidebar.header("Cohort Filters")
    all_segments = df_rfm['segment'].unique().tolist()
    selected_segments = st.sidebar.multiselect("Select Segments:", all_segments, default=all_segments)
    filtered = df_rfm[df_rfm['segment'].isin(selected_segments)]

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    total_rev = filtered['monetary'].sum()
    avg_spend = filtered['monetary'].mean() if len(filtered) > 0 else 0
    at_risk_count = (filtered['segment'] == 'At Risk').sum()
    champ_share = (filtered[filtered['segment'] == 'Champions']['monetary'].sum() / total_rev * 100) if total_rev > 0 else 0

    c1.metric("Gross Revenue", f"${total_rev:,.2f}")
    c2.metric("Mean Spend / User", f"${avg_spend:,.2f}")
    c3.metric("At-Risk Accounts", f"{at_risk_count}", delta="Requires Retention", delta_color="inverse")
    c4.metric("Champions Rev Share", f"{champ_share:.1f}%")

    st.divider()

    # Visualizations
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Revenue Contribution by Segment")
        seg_rev = filtered.groupby('segment')['monetary'].sum().reset_index()
        fig_pie = px.pie(seg_rev, names='segment', values='monetary', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("🎯 Recency vs Total Spend")
        fig_scatter = px.scatter(
            filtered, 
            x='recency', 
            y='monetary', 
            color='segment', 
            size='frequency',
            labels={'recency': 'Recency (Days Since Last Order)', 'monetary': 'Total Sales ($)'},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Processed Data Table
    st.divider()
    st.subheader("📋 Segmented Customer Data Table")
    st.dataframe(filtered.head(100), use_container_width=True)

    # Retention Experimentation Module
    st.divider()
    st.subheader("🧪 Live Retention Campaign Experimentation (A/B Test)")
    st.markdown("Testing coupon intervention on **At-Risk** customers against baseline control.")

    sim1, sim2 = st.columns(2)
    with sim1:
        sample_size = st.slider("Cohort Sample Size", 200, 2000, 500, step=50)
        control_rate = st.slider("Control Conversion Rate (%)", 1.0, 15.0, 4.0, step=0.1)
    with sim2:
        treatment_rate = st.slider("Treatment (Coupon) Conversion Rate (%)", 1.0, 20.0, 7.2, step=0.1)
        alpha = st.selectbox("Significance Level (Alpha):", [0.05, 0.01])

    ctrl_conv = int(sample_size * (control_rate / 100))
    treat_conv = int(sample_size * (treatment_rate / 100))
    table = [[ctrl_conv, sample_size - ctrl_conv], [treat_conv, sample_size - treat_conv]]
    stat, p_val, _, _ = chi2_contingency(table)
    uplift = ((treatment_rate - control_rate) / control_rate) * 100

    st.write(f"**Observed Uplift:** `{uplift:+.2f}%` | **Calculated p-value:** `{p_val:.5f}`")
    if p_val < alpha:
        st.success(f"✅ Statistically Significant: Retention offer provides measurable uplift ($p = {p_val:.5f} < {alpha}$).")
    else:
        st.warning(f"⚠️ Inconclusive: Uplift is not statistically significant ($p = {p_val:.5f} \ge {alpha}$).")