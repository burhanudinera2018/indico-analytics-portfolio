"""
Quick Import - Tanpa ribet foreign key
"""

import pandas as pd
from sqlalchemy import create_engine, text

# Koneksi ke database (sesuaikan dengan konfigurasi Anda)
engine = create_engine('postgresql:///indico_db?host=localhost')

print("📥 Starting import...")

# Baca CSV
df_users = pd.read_csv('../data/users.csv')
df_activities = pd.read_csv('../data/user_activity_logs.csv')
df_transactions = pd.read_csv('../data/transactions.csv')

print(f"Data loaded: {len(df_users)} users, {len(df_activities)} logs, {len(df_transactions)} transactions")

# Reset database dengan urutan benar
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS transactions CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS user_activity_logs CASCADE;"))
    conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    conn.commit()
    print("✅ Tables dropped")

# Import dengan urutan benar
df_users.to_sql('users', engine, if_exists='append', index=False)
print(f"✅ Users imported: {len(df_users)}")

df_activities.to_sql('user_activity_logs', engine, if_exists='append', index=False)
print(f"✅ Activity logs imported: {len(df_activities)}")

df_transactions.to_sql('transactions', engine, if_exists='append', index=False)
print(f"✅ Transactions imported: {len(df_transactions)}")

# Verifikasi
with engine.connect() as conn:
    users_count = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    print(f"\n🎉 Final verification: {users_count} users in database")

print("Done!")