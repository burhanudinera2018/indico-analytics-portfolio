"""
Export data from local PostgreSQL to Supabase Cloud
"""

from sqlalchemy import create_engine, text
import pandas as pd
import urllib.parse

# ============================================
# KONFIGURASI - SESUAI DENGAN SCREENSHOT ANDA
# ============================================

# Local database (sumber data) - sudah benar untuk macOS
LOCAL_DB = 'postgresql:///indico_db?host=localhost'

# Supabase configuration - BERDASARKAN SCREENSHOT ANDA
SUPABASE_PROJECT_REF = "njirsehbdiuinnbwegni"  # ✅ Pastikan ini benar
SUPABASE_PASSWORD = "S3cr3t_l1v3_4dm1n"  # Ganti dengan password Supabase Anda
SUPABASE_REGION = "ap-southeast-1"

# ⚠️ INI YANG PALING PENTING - Hostname benar dari screenshot
SUPABASE_HOST = "aws-1-ap-southeast-1.pooler.supabase.com"  # ✅ BENAR

# Build connection string
SUPABASE_USER = f"postgres.{SUPABASE_PROJECT_REF}"

# Encode password jika ada karakter spesial
encoded_password = urllib.parse.quote(SUPABASE_PASSWORD, safe='')

SUPABASE_URL = f"postgresql://{SUPABASE_USER}:{encoded_password}@{SUPABASE_HOST}:5432/postgres"

# ============================================
# EKSEKUSI EXPORT
# ============================================

print("="*60)
print("📤 EXPORT DATA TO SUPABASE")
print("="*60)

# Tampilkan konfigurasi yang digunakan
print(f"\n📋 Konfigurasi yang digunakan:")
print(f"   Host: {SUPABASE_HOST}")
print(f"   User: {SUPABASE_USER}")
print(f"   Project Ref: {SUPABASE_PROJECT_REF}")

# 1. Koneksi ke local database
print("\n📖 Reading data from local database...")
try:
    engine_local = create_engine(LOCAL_DB)
    
    df_users = pd.read_sql("SELECT * FROM users", engine_local)
    df_activities = pd.read_sql("SELECT * FROM user_activity_logs", engine_local)
    df_transactions = pd.read_sql("SELECT * FROM transactions", engine_local)
    
    print(f"   ✅ Users: {len(df_users)} rows")
    print(f"   ✅ Activities: {len(df_activities)} rows")
    print(f"   ✅ Transactions: {len(df_transactions)} rows")
    
    if len(df_users) == 0:
        print("\n❌ ERROR: Local database KOSONG!")
        exit(1)
        
except Exception as e:
    print(f"\n❌ Gagal baca dari local database: {e}")
    exit(1)

# 2. Koneksi ke Supabase
print("\n🔌 Connecting to Supabase...")

try:
    engine_supabase = create_engine(SUPABASE_URL)
    with engine_supabase.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("   ✅ Connected to Supabase!")
except Exception as e:
    print(f"\n❌ Failed to connect to Supabase: {e}")
    print(f"\n📋 Connection string yang digunakan:")
    print(f"   {SUPABASE_URL.replace(encoded_password, '******')}")
    exit(1)

# 3. Upload data
print("\n📤 Uploading to Supabase...")

try:
    with engine_supabase.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_activity_logs CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    print("   ✅ Existing tables dropped")
except Exception as e:
    print(f"   ⚠️ No tables to drop: {e}")

# Upload users
df_users.to_sql('users', engine_supabase, if_exists='append', index=False)
print("   ✅ Users table created and data inserted")

# Upload activities
df_activities.to_sql('user_activity_logs', engine_supabase, if_exists='append', index=False)
print("   ✅ Activities table created and data inserted")

# Upload transactions
df_transactions.to_sql('transactions', engine_supabase, if_exists='append', index=False)
print("   ✅ Transactions table created and data inserted")

# 4. Verifikasi
print("\n📊 Verifikasi data di Supabase:")
with engine_supabase.connect() as conn:
    users_count = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    activities_count = conn.execute(text("SELECT COUNT(*) FROM user_activity_logs")).fetchone()[0]
    transactions_count = conn.execute(text("SELECT COUNT(*) FROM transactions")).fetchone()[0]
    
    print(f"   Users: {users_count} rows")
    print(f"   Activities: {activities_count} rows")
    print(f"   Transactions: {transactions_count} rows")

print("\n" + "="*60)
print("🎉 Export to Supabase completed successfully!")
print("="*60)

# 5. Tampilkan connection string untuk Streamlit secrets
print("\n📋 Copy ini untuk Streamlit Secrets (Settings → Secrets):")
print("-"*60)
print(f"SUPABASE_URL = \"{SUPABASE_URL}\"")
print("-"*60)