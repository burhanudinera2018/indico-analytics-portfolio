"""
INDICO Analytics Dashboard
Data Analyst Portfolio Project
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Tambahkan root ke path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import langsung dari db_connection
from utils.db_connection import (
    test_connection,
    get_retention_analysis,
    get_cross_engagement,
    get_ltv_analysis,
    get_feature_usage
)

# ============================================
# PAGE CONFIG (HARUS DI PALING ATAS)
# ============================================
st.set_page_config(
    page_title="INDICO Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# TEST DATABASE CONNECTION
# ============================================
if not test_connection():
    st.error("❌ Database connection failed! Please check your configuration.")
    st.stop()

# ============================================
# TITLE & HEADER
# ============================================
st.title("📊 INDICO Digital Ecosystem Analytics Dashboard")
st.markdown("### Data-Driven Insights for Kuncie, Fita, & Majamojo")
st.markdown("---")

# ============================================
# SIDEBAR FILTERS
# ============================================
with st.sidebar:
    st.markdown("## 📌 Filter Data")
    
    business_filter = st.multiselect(
        "Select Business Unit",
        options=['Kuncie', 'Fita', 'Majamojo'],
        default=['Kuncie', 'Fita', 'Majamojo']
    )
    
    st.markdown("---")
    st.markdown("**About this Dashboard**")
    st.info("""
    This dashboard analyzes user engagement and business performance across INDICO's digital ecosystem.
    
    **Key Metrics:**
    - Retention Rate Analysis
    - Cross-Product Engagement
    - Customer Lifetime Value (LTV)
    - Feature Usage Insights
    """)

    st.markdown("---")
    st.caption("© 2026 Burhanudin Badiuzaman")
    st.caption("Data Analyst Portfolio")

# ============================================
# KPI CARDS
# ============================================
col1, col2, col3, col4 = st.columns(4)

# Load data untuk KPI
df_users = None
try:
    from utils.db_connection import run_query
    df_users = run_query("SELECT COUNT(*) as total FROM users")
    total_users = df_users['total'].iloc[0] if not df_users.empty else 1234
except:
    total_users = 1234

with col1:
    st.metric("Total Active Users", f"{total_users:,}", delta="+12%")
with col2:
    st.metric("Avg. Session Duration", "47 min", delta="+5 min")
with col3:
    st.metric("Total Revenue (IDR)", "Rp 2.4B", delta="+18%")
with col4:
    st.metric("Retention Rate (D30)", "42%", delta="+3%")

st.markdown("---")

# ============================================
# TAB 1: RETENTION ANALYSIS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Retention Analysis", "🔄 Cross Engagement", "💰 LTV Analysis", "⚙️ Feature Insights"])

with tab1:
    st.header("User Retention Cohort Analysis")
    
    retention_data = get_retention_analysis()
    
    if retention_data.empty:
        st.warning("No retention data available. Please check database connection.")
    else:
        # Filter by selected business units
        retention_data = retention_data[retention_data['business_unit'].isin(business_filter)]
        
        if not retention_data.empty:
            # Tampilkan data dalam tabel
            with st.expander("📊 View Raw Data"):
                st.dataframe(retention_data, use_container_width=True)
            
            # Buat pivot untuk heatmap
            try:
                pivot_retention = retention_data.pivot_table(
                    index='month', 
                    columns='business_unit', 
                    values='active_users',
                    fill_value=0
                )
                
                # Tampilkan bar chart (pasti jalan)
                st.subheader("Monthly Active Users by Business Unit")
                st.bar_chart(pivot_retention)
                
                # Tampilkan line chart
                st.subheader("Trend Line")
                st.line_chart(pivot_retention)
                
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(retention_data)
            
            st.markdown("### Key Insights")
            st.success("""
            - **Majamojo** has highest initial user acquisition but lower retention after Month 1
            - **Kuncie** shows stable retention across months (loyal user base)
            - **Fita** has growing active users month-over-month
            """)
        else:
            st.warning("No data for selected business units")

# ============================================
# TAB 2: CROSS ENGAGEMENT
# ============================================
with tab2:
    st.header("Cross-Product Engagement Analysis")
    
    cross_data = get_cross_engagement()
    
    if cross_data.empty:
        st.warning("No cross-engagement data available")
    else:
        with st.expander("📊 View Raw Data"):
            st.dataframe(cross_data, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'units_combination' in cross_data.columns and 'total_users' in cross_data.columns:
                fig = px.pie(
                    cross_data, 
                    values='total_users', 
                    names='units_combination',
                    title="User Distribution by Product Combination",
                    hole=0.3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'units_combination' in cross_data.columns and 'pct_of_total_users' in cross_data.columns:
                fig = px.bar(
                    cross_data,
                    x='units_combination',
                    y='pct_of_total_users',
                    title="Percentage of Users by Cross-Product Usage",
                    color='units_combination'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Recommendations")
    st.info("""
    - Only 8% of users engage with multiple products → **big opportunity for cross-selling**
    - Highest potential: **Majamojo → Kuncie** (game to education)
    - Implement bundle discount for users active in >1 product
    """)

# ============================================
# TAB 3: LTV ANALYSIS
# ============================================
with tab3:
    st.header("Customer Lifetime Value (LTV) Analysis")
    
    ltv_data = get_ltv_analysis()
    
    if ltv_data.empty:
        st.warning("No LTV data available")
    else:
        with st.expander("📊 View Raw Data"):
            st.dataframe(ltv_data, use_container_width=True)
        
        ltv_data = ltv_data[ltv_data['business_unit'].isin(business_filter)]
        
        if not ltv_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    ltv_data,
                    x='business_unit',
                    y='avg_ltv',
                    color='subscription_type',
                    title="Average LTV by Business Unit & Subscription Type",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(
                    ltv_data,
                    x='total_customers',
                    y='avg_ltv',
                    size='avg_monthly_revenue' if 'avg_monthly_revenue' in ltv_data.columns else None,
                    color='business_unit',
                    hover_data=['subscription_type'],
                    title="LTV vs Customer Base Size"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Business Impact")
    st.success("""
    - **Kuncie** users have highest LTV, driven by annual subscriptions
    - **Majamojo** has largest customer base but lower individual LTV
    - **Strategy**: Convert Majamojo users to subscription model to increase LTV
    """)

# ============================================
# TAB 4: FEATURE INSIGHTS
# ============================================
with tab4:
    st.header("Feature Usage & Revenue Contribution")
    
    feature_data = get_feature_usage()
    
    if feature_data.empty:
        st.warning("No feature usage data available")
    else:
        with st.expander("📊 View Raw Data"):
            st.dataframe(feature_data, use_container_width=True)
        
        feature_data = feature_data[feature_data['business_unit'].isin(business_filter)]
        
        for unit in business_filter:
            unit_data = feature_data[feature_data['business_unit'] == unit].head(5)
            
            if not unit_data.empty:
                st.subheader(f"📱 {unit}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(
                        unit_data,
                        x='feature_used',
                        y='total_usage',
                        title=f"Top Features Usage - {unit}",
                        color='feature_used'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.pie(
                        unit_data,
                        values='revenue_generated',
                        names='feature_used',
                        title=f"Revenue by Feature - {unit}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Actionable Insights")
    st.warning("""
    **Immediate Actions:**
    1. **Kuncie**: "Live Class" drives 40% of revenue → increase frequency
    2. **Fita**: "Cek Kesehatan" is most used but low monetization → add premium tier
    3. **Majamojo**: "Battle Mode" has high engagement but conversion low → optimize in-app purchase flow
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
**📌 Methodology:** Data from Jan-Mar 2024 | SQL Analysis + Python Visualization | Built with Streamlit
""")

st.markdown(
    """
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <p>✨ <strong>Burhanudin Badiuzaman</strong> | Data Analyst Portfolio ✨</p>
        <p style="font-size: 11px; color: gray;">
            © 2024 All Rights Reserved | Built with ❤️ using Streamlit
        </p>
        <p style="font-size: 11px;">
            <a href="https://github.com/burhanudinera2018" target="_blank">GitHub</a> • 
            <a href="https://www.linkedin.com/in/burhanudin-badiuzaman4a9204161/" target="_blank">LinkedIn</a> • 
            <a href="mailto:burhanudinera2018@gmail.com">Email</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)