"""
Import data dari CSV ke PostgreSQL
Letakkan di: database/import_data.py
Jalankan dari: database/ (python import_data.py)
"""

import pandas as pd
import sys
import os

# Tambahkan root project ke path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_config import get_engine, test_connection

def import_users():
    """Import data users.csv ke tabel users"""
    print("📤 Importing users...")
    
    # Path yang benar: dari folder database, naik ke root, lalu ke data
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.csv')
    
    if not os.path.exists(csv_path):
        print(f"   ❌ File tidak ditemukan: {csv_path}")
        print("   💡 Pastikan dataset sudah di-generate di folder data/")
        return False
    
    df = pd.read_csv(csv_path)
    engine = get_engine()
    
    df.to_sql('users', engine, if_exists='replace', index=False)
    print(f"   ✅ Imported {len(df)} users")
    return True

def import_activities():
    """Import data user_activity_logs.csv"""
    print("📤 Importing activity logs...")
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'user_activity_logs.csv')
    
    if not os.path.exists(csv_path):
        print(f"   ❌ File tidak ditemukan: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    engine = get_engine()
    
    df.to_sql('user_activity_logs', engine, if_exists='replace', index=False)
    print(f"   ✅ Imported {len(df)} activity logs")
    return True

def import_transactions():
    """Import data transactions.csv"""
    print("📤 Importing transactions...")
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'transactions.csv')
    
    if not os.path.exists(csv_path):
        print(f"   ❌ File tidak ditemukan: {csv_path}")
        return False
    
    df = pd.read_csv(csv_path)
    engine = get_engine()
    
    df.to_sql('transactions', engine, if_exists='replace', index=False)
    print(f"   ✅ Imported {len(df)} transactions")
    return True

def verify_import():
    """Verifikasi data yang sudah diimport"""
    engine = get_engine()
    
    with engine.connect() as conn:
        from sqlalchemy import text
        
        users_count = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        activities_count = conn.execute(text("SELECT COUNT(*) FROM user_activity_logs")).fetchone()[0]
        transactions_count = conn.execute(text("SELECT COUNT(*) FROM transactions")).fetchone()[0]
        
        print("\n📊 Verifikasi data:")
        print(f"   Users: {users_count} rows")
        print(f"   Activity Logs: {activities_count} rows")
        print(f"   Transactions: {transactions_count} rows")
        
        # Cek sample data
        sample = conn.execute(text("SELECT * FROM users LIMIT 3")).fetchall()
        print("\n📋 Sample data (users):")
        for row in sample:
            print(f"   {row}")

if __name__ == "__main__":
    print("="*50)
    print("Import Data ke PostgreSQL")
    print("="*50)
    
    if test_connection():
        success = True
        success &= import_users()
        success &= import_activities()
        success &= import_transactions()
        
        if success:
            verify_import()
            print("\n🎉 Semua data berhasil diimport!")
        else:
            print("\n❌ Beberapa file CSV tidak ditemukan.")
            print("💡 Jalankan dulu: python scripts/generate_dataset.py")
    else:
        print("\n❌ Gagal koneksi ke database.")
        print("💡 Pastikan PostgreSQL sudah running dan database indico_db sudah dibuat")