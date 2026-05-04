import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db_connection import *

# Page config
st.set_page_config(
    page_title="INDICO Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📊 INDICO Digital Ecosystem Analytics Dashboard")
st.markdown("### Data-Driven Insights for Kuncie, Fita, & Majamojo")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=INDICO", use_column_width=True)
    st.markdown("## Filter Data")
    
    business_filter = st.multiselect(
        "Select Business Unit",
        options=['Kuncie', 'Fita', 'Majamojo'],
        default=['Kuncie', 'Fita', 'Majamojo']
    )
    
    date_range = st.date_input(
        "Date Range",
        value=(pd.Timestamp('2024-01-01'), pd.Timestamp('2024-03-31'))
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

# Main content
col1, col2, col3, col4 = st.columns(4)

# KPI Cards
with col1:
    st.metric("Total Active Users", "1,234", delta="+12%")
with col2:
    st.metric("Avg. Session Duration", "47 min", delta="+5 min")
with col3:
    st.metric("Total Revenue (IDR)", "Rp 2.4B", delta="+18%")
with col4:
    st.metric("Retention Rate (D30)", "42%", delta="+3%")

st.markdown("---")

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["📈 Retention Analysis", "🔄 Cross Engagement", "💰 LTV Analysis", "⚙️ Feature Insights"])

with tab1:
    st.header("User Retention Cohort Analysis")
    
    retention_data = get_retention_analysis()
    
    # Filter by selected business units
    retention_data = retention_data[retention_data['business_unit'].isin(business_filter)]
    
    # Create heatmap
    pivot_retention = retention_data.pivot_table(
        index='cohort_month', 
        columns='business_unit', 
        values='active_users',
        fill_value=0
    )
    
    fig = px.imshow(
        pivot_retention.T,
        text_auto=True,
        aspect="auto",
        title="Monthly Active Users by Cohort",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Key Insights")
    st.success("""
    - **Majamojo** has highest initial user acquisition but lower retention after Month 1
    - **Kuncie** shows stable retention across months (loyal user base)
    - **Fita** has growing active users month-over-month
    """)

with tab2:
    st.header("Cross-Product Engagement Analysis")
    
    cross_data = get_cross_engagement()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            cross_data, 
            values='total_users', 
            names='units_combination',
            title="User Distribution by Product Combination",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
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

with tab3:
    st.header("Customer Lifetime Value (LTV) Analysis")
    
    ltv_data = get_ltv_analysis()
    ltv_data = ltv_data[ltv_data['business_unit'].isin(business_filter)]
    
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
            size='avg_monthly_revenue',
            color='business_unit',
            hover_data=['subscription_type'],
            title="LTV vs Customer Base Size"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Business Impact")
    st.success("""
    - **Kuncie** users have highest LTV (Rp 250k/month), driven by annual subscriptions
    - **Majamojo** has largest customer base but lower individual LTV
    - **Strategy**: Convert Majamojo users to subscription model to increase LTV by 2x
    """)

with tab4:
    st.header("Feature Usage & Revenue Contribution")
    
    feature_data = get_feature_usage()
    feature_data = feature_data[feature_data['business_unit'].isin(business_filter)]
    
    for unit in business_filter:
        st.subheader(f"📱 {unit}")
        unit_data = feature_data[feature_data['business_unit'] == unit].head(5)
        
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

# Footer
st.markdown("---")
st.markdown("""
**📌 Methodology:** Data from Jan-Mar 2024 | SQL Analysis + Python Visualization | Built with Streamlit
""")