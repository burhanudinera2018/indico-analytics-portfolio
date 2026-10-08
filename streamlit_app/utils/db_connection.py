"""
Database connection for INDICO Analytics
Support local, cloud (Supabase), dan cadangan snapshot CSV.

Alur run_query():
1. Coba database (Supabase di Streamlit Cloud, atau PostgreSQL lokal).
2. Jika gagal, baca hasil query yang sama dari folder data_snapshot/.
3. Detail error hanya dicatat di log (Manage app), tidak ditampilkan ke pengunjung.

Membuat/memperbarui snapshot (di laptop, sekali saja):
    SIMPAN_SNAPSHOT=1 streamlit run streamlit_app/app.py
"""

import hashlib
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "data_snapshot"
SIMPAN_SNAPSHOT = os.environ.get("SIMPAN_SNAPSHOT") == "1"
_status = {"pakai_snapshot": False}


def _log(pesan: str) -> None:
    """Catat ke log Streamlit (terlihat di Manage app), bukan ke layar pengunjung."""
    print(f"[db_connection] {pesan}", flush=True)


@st.cache_resource
def _buat_engine():
    """Engine hanya di-cache jika BERHASIL; kegagalan (exception) tidak di-cache,
    sehingga aplikasi otomatis mencoba lagi tanpa perlu Reboot."""
    url = os.environ.get("SUPABASE_URL") or "postgresql:///indico_db?host=localhost"
    args = {"connect_timeout": 5} if url.startswith("postgresql") else {}
    engine = create_engine(url, connect_args=args, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine


def get_engine():
    """Get database engine - None jika database tidak bisa dihubungi."""
    try:
        return _buat_engine()
    except Exception as e:
        _log(f"Koneksi database gagal: {e}")
        return None


def _file_snapshot(query: str) -> Path:
    """Nama file CSV unik per query (spasi dinormalkan agar stabil)."""
    kunci = re.sub(r"\s+", " ", query).strip()
    return SNAPSHOT_DIR / f"{hashlib.sha1(kunci.encode()).hexdigest()[:12]}.csv"


def run_query(query):
    """Execute query and return DataFrame (database, atau snapshot bila database gagal)."""
    engine = get_engine()
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            if SIMPAN_SNAPSHOT:
                SNAPSHOT_DIR.mkdir(exist_ok=True)
                df.to_csv(_file_snapshot(query), index=False)
                _log(f"Snapshot disimpan: {_file_snapshot(query).name} ({len(df)} baris)")
            return df
        except Exception as e:
            _log(f"Query gagal, beralih ke snapshot: {e}")

    berkas = _file_snapshot(query)
    if berkas.exists():
        _status["pakai_snapshot"] = True
        return pd.read_csv(berkas)
    _log(f"Snapshot tidak ditemukan untuk query ini ({berkas.name})")
    return pd.DataFrame()


def test_connection():
    """True jika database terhubung."""
    engine = get_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        _log(f"Tes koneksi gagal: {e}")
        return False


def mode_data():
    """'live' (database), 'snapshot' (cadangan CSV), atau 'none' (tidak ada data)."""
    if test_connection():
        return "live"
    if SNAPSHOT_DIR.exists() and any(SNAPSHOT_DIR.glob("*.csv")):
        return "snapshot"
    return "none"


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
