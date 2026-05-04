# verify_supabase.py
from sqlalchemy import create_engine, text
import os

# Ganti dengan connection string Anda
SUPABASE_URL = "postgresql://postgres.njirshebdiuinnbwegni:password_anda@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

engine = create_engine(SUPABASE_URL)

with engine.connect() as conn:
    # Cek jumlah data
    users = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    activities = conn.execute(text("SELECT COUNT(*) FROM user_activity_logs")).fetchone()[0]
    
    print(f"Users: {users}")
    print(f"Activities: {activities}")
    
    if users == 0:
        print("⚠️ Database kosong! Perlu import data.")
    else:
        print("✅ Data tersedia!")