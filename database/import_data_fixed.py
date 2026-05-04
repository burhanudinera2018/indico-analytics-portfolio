"""
Import data ke PostgreSQL - Fixed version
Jalankan dari folder database
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# Tambahkan root ke path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Koneksi database
engine = create_engine('postgresql:///indico_db?host=localhost')

def import_data():
    """Import semua data dengan urutan yang benar"""
    
    # Path ke file CSV
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    print("="*50)
    print("IMPORT DATA KE DATABASE")
    print("="*50)
    
    # 1. Import users (parent table)
    users_file = os.path.join(data_dir, 'users.csv')
    if not os.path.exists(users_file):
        print(f"❌ File tidak ditemukan: {users_file}")
        print("   Jalankan dulu: python scripts/generate_dataset.py")
        return False
    
    df_users = pd.read_csv(users_file)
    df_users.to_sql('users', engine, if_exists='append', index=False)
    print(f"✅ Users imported: {len(df_users)} rows")
    
    # 2. Import activity logs (child table)
    activities_file = os.path.join(data_dir, 'user_activity_logs.csv')
    df_activities = pd.read_csv(activities_file)
    df_activities.to_sql('user_activity_logs', engine, if_exists='append', index=False)
    print(f"✅ Activity logs imported: {len(df_activities)} rows")
    
    # 3. Import transactions (child table)
    transactions_file = os.path.join(data_dir, 'transactions.csv')
    df_transactions = pd.read_csv(transactions_file)
    df_transactions.to_sql('transactions', engine, if_exists='append', index=False)
    print(f"✅ Transactions imported: {len(df_transactions)} rows")
    
    return True

def verify():
    """Verifikasi data setelah import"""
    print("\n" + "="*50)
    print("VERIFIKASI DATA")
    print("="*50)
    
    with engine.connect() as conn:
        users = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
        activities = conn.execute(text("SELECT COUNT(*) FROM user_activity_logs")).fetchone()[0]
        transactions = conn.execute(text("SELECT COUNT(*) FROM transactions")).fetchone()[0]
        
        print(f"📊 users: {users} rows")
        print(f"📊 user_activity_logs: {activities} rows")
        print(f"📊 transactions: {transactions} rows")
        
        # Sample data
        if users > 0:
            sample = conn.execute(text("SELECT user_id, business_unit, registration_date FROM users LIMIT 3"))
            print("\n📝 Sample users:")
            for row in sample:
                print(f"   {row[0]} | {row[1]} | {row[2]}")

if __name__ == "__main__":
    if import_data():
        verify()
        print("\n🎉 Database import completed successfully!")
    else:
        print("\n❌ Import failed!")