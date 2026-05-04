import streamlit as st
import pandas as pd
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database.init_db import get_engine

@st.cache_resource
def init_connection():
    return get_engine()

def run_query(query):
    engine = init_connection()
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn)

def get_retention_analysis():
    """Retention analysis - simplified version"""
    query = """
    WITH user_cohort AS (
        SELECT 
            user_id,
            business_unit,
            DATE_TRUNC('month', registration_date) AS cohort_month
        FROM users
    ),
    user_activity AS (
        SELECT 
            ua.user_id,
            u.business_unit,
            u.cohort_month,
            DATE_TRUNC('month', ua.activity_date) AS activity_month
        FROM user_activity_logs ua
        JOIN user_cohort u ON ua.user_id = u.user_id
        WHERE ua.activity_date >= u.cohort_month
    )
    SELECT 
        cohort_month::DATE as cohort_month,
        business_unit,
        activity_month,
        COUNT(DISTINCT user_id) AS active_users
    FROM user_activity
    GROUP BY cohort_month, business_unit, activity_month
    ORDER BY cohort_month, business_unit, activity_month
    """
    try:
        return run_query(query)
    except Exception as e:
        print(f"Error in retention query: {e}")
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=['cohort_month', 'business_unit', 'activity_month', 'active_users'])
    query = """
    WITH user_cohort AS (
        SELECT 
            user_id,
            business_unit,
            DATE_TRUNC('month', registration_date) AS cohort_month
        FROM users
    ),
    user_activity_cohort AS (
        SELECT 
            ua.user_id,
            u.business_unit,
            u.cohort_month,
            DATE_TRUNC('month', ua.activity_date) AS activity_month,
            EXTRACT(MONTH FROM AGE(ua.activity_date, u.registration_date)) AS month_number
        FROM user_activity_logs ua
        JOIN user_cohort u ON ua.user_id = u.user_id
        WHERE ua.activity_date >= u.registration_date
    )
    SELECT 
        cohort_month,
        business_unit,
        month_number,
        COUNT(DISTINCT user_id) AS active_users
    FROM user_activity_cohort
    GROUP BY cohort_month, business_unit, month_number
    ORDER BY cohort_month, business_unit, month_number
    """
    return run_query(query)

def get_cross_engagement():
    query = """
    WITH multi_product_users AS (
        SELECT 
            user_id,
            COUNT(DISTINCT business_unit) AS total_units_used,
            STRING_AGG(DISTINCT business_unit, ', ' ORDER BY business_unit) AS units_combination
        FROM user_activity_logs
        GROUP BY user_id
        HAVING COUNT(DISTINCT business_unit) > 1
    )
    SELECT 
        units_combination,
        COUNT(user_id) AS total_users,
        ROUND(100.0 * COUNT(user_id) / (SELECT COUNT(DISTINCT user_id) FROM user_activity_logs), 2) AS pct_of_total_users
    FROM multi_product_users
    GROUP BY units_combination
    ORDER BY total_users DESC
    """
    return run_query(query)

def get_ltv_analysis():
    query = """
    WITH user_revenue AS (
        SELECT 
            t.user_id,
            u.business_unit,
            t.subscription_type,
            SUM(t.amount) AS total_revenue,
            COUNT(DISTINCT DATE_TRUNC('month', t.transaction_date)) AS active_months
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        GROUP BY t.user_id, u.business_unit, t.subscription_type
    )
    SELECT 
        business_unit,
        subscription_type,
        COUNT(user_id) AS total_customers,
        ROUND(AVG(total_revenue), 2) AS avg_ltv,
        ROUND(AVG(total_revenue / NULLIF(active_months, 0)), 2) AS avg_monthly_revenue
    FROM user_revenue
    GROUP BY business_unit, subscription_type
    ORDER BY business_unit, avg_ltv DESC
    """
    return run_query(query)

def get_feature_usage():
    query = """
    SELECT 
        business_unit,
        feature_used,
        COUNT(*) AS total_usage,
        COUNT(DISTINCT user_id) AS unique_users,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY business_unit), 2) AS usage_percentage,
        SUM(transaction_amt) AS revenue_generated
    FROM user_activity_logs
    WHERE feature_used IS NOT NULL
    GROUP BY business_unit, feature_used
    ORDER BY business_unit, total_usage DESC
    """
    return run_query(query)