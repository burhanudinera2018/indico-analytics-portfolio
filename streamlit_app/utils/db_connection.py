"""
Database connection for INDICO Analytics
"""

import os
import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

@st.cache_resource
def get_engine():
    """Get database engine from environment"""
    
    # Debug: Tampilkan environment variables yang tersedia
    st.write("🔍 Checking environment...")
    
    # Cek SUPABASE_URL dari secrets
    supabase_url = os.environ.get("SUPABASE_URL")
    
    if supabase_url:
        st.success("✅ SUPABASE_URL found in secrets!")
        # Tampilkan host saja (tanpa password)
        if "@" in supabase_url:
            host_part = supabase_url.split("@")[1].split("/")[0]
            st.info(f"   Connecting to: {host_part}")
        
        try:
            engine = create_engine(supabase_url)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            st.success("✅ Database connection successful!")
            return engine
        except Exception as e:
            st.error(f"❌ Failed to connect: {e}")
            st.code(f"Error type: {type(e).__name__}")
            return None
    else:
        st.error("❌ SUPABASE_URL not found in secrets!")
        st.info("Please add SUPABASE_URL in Streamlit Cloud Settings → Secrets")
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

# ============================================
# SIMPLE QUERIES (pasti jalan)
# ============================================

def get_retention_analysis():
    """Simple retention query"""
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
    """Cross engagement query"""
    query = """
    SELECT 
        business_unit,
        COUNT(DISTINCT user_id) AS total_users
    FROM user_activity_logs
    GROUP BY business_unit
    ORDER BY total_users DESC
    """
    return run_query(query)

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