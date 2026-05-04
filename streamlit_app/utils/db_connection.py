"""
Database connection for INDICO Analytics
Support both local and cloud (Supabase)
"""

import os
import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

@st.cache_resource
def get_engine():
    """Get database engine - cached for performance"""
    
    # Untuk Streamlit Cloud (Supabase)
    supabase_url = os.environ.get("SUPABASE_URL")
    if supabase_url:
        try:
            engine = create_engine(supabase_url)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception as e:
            st.error(f"❌ Cannot connect to Supabase: {e}")
            return None
    
    # Untuk local development
    try:
        engine = create_engine('postgresql:///indico_db?host=localhost')
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Cannot connect to local database: {e}")
        return None

def run_query(query):
    """Execute query and return DataFrame"""
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()
    
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(text(query), conn)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

def test_connection():
    """Test database connection"""
    engine = get_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except:
        return False

# ============================================
# MAIN ANALYSIS FUNCTIONS
# ============================================

def get_retention_analysis():
    """Retention analysis - monthly active users"""
    query = """
    SELECT 
        DATE_TRUNC('month', activity_date) AS month,
        business_unit,
        COUNT(DISTINCT user_id) AS active_users
    FROM user_activity_logs
    GROUP BY DATE_TRUNC('month', activity_date), business_unit
    ORDER BY month, business_unit
    """
    return run_query(query)

def get_cross_engagement():
    """Cross engagement analysis"""
    query = """
    WITH user_products AS (
        SELECT 
            user_id,
            COUNT(DISTINCT business_unit) AS product_count,
            STRING_AGG(DISTINCT business_unit, ', ' ORDER BY business_unit) AS units_combination
        FROM user_activity_logs
        GROUP BY user_id
    )
    SELECT 
        units_combination,
        COUNT(user_id) AS total_users,
        ROUND(100.0 * COUNT(user_id) / (SELECT COUNT(DISTINCT user_id) FROM user_activity_logs), 2) AS pct_of_total_users
    FROM user_products
    WHERE product_count > 1
    GROUP BY units_combination
    ORDER BY total_users DESC
    """
    return run_query(query)

def get_ltv_analysis():
    """LTV analysis by business unit"""
    query = """
    SELECT 
        u.business_unit,
        COALESCE(t.subscription_type, 'No Subscription') AS subscription_type,
        COUNT(DISTINCT t.user_id) AS total_customers,
        COALESCE(AVG(t.amount), 0) AS avg_ltv,
        COALESCE(AVG(t.amount), 0) AS avg_monthly_revenue
    FROM users u
    LEFT JOIN transactions t ON u.user_id = t.user_id
    GROUP BY u.business_unit, t.subscription_type
    ORDER BY u.business_unit, avg_ltv DESC
    """
    return run_query(query)

def get_feature_usage():
    """Feature usage analysis"""
    query = """
    SELECT 
        business_unit,
        feature_used,
        COUNT(*) AS total_usage,
        COUNT(DISTINCT user_id) AS unique_users,
        SUM(transaction_amt) AS revenue_generated
    FROM user_activity_logs
    WHERE feature_used IS NOT NULL
    GROUP BY business_unit, feature_used
    ORDER BY business_unit, total_usage DESC
    LIMIT 20
    """
    return run_query(query)