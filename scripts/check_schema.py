"""
Check database schema - tanpa perlu psql
"""

from sqlalchemy import create_engine, text

# Koneksi ke database
engine = create_engine('postgresql:///indico_db?host=localhost')

print("="*50)
print("CHECKING DATABASE SCHEMA")
print("="*50)

with engine.connect() as conn:
    # 1. Cek daftar semua tabel
    print("\n📋 Tables in database:")
    tables = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))
    for table in tables:
        print(f"   - {table[0]}")
    
    # 2. Cek struktur tabel users
    print("\n📋 Columns in 'users' table:")
    columns = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """))
    for col in columns:
        print(f"   - {col[0]} ({col[1]}) nullable={col[2]}")
    
    # 3. Cek struktur tabel user_activity_logs
    print("\n📋 Columns in 'user_activity_logs' table:")
    columns = conn.execute(text("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'user_activity_logs'
        ORDER BY ordinal_position
    """))
    for col in columns:
        print(f"   - {col[0]} ({col[1]}) nullable={col[2]}")
    
    # 4. Cek jumlah data
    print("\n📊 Row counts:")
    users_count = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    activities_count = conn.execute(text("SELECT COUNT(*) FROM user_activity_logs")).fetchone()[0]
    transactions_count = conn.execute(text("SELECT COUNT(*) FROM transactions")).fetchone()[0]
    print(f"   - users: {users_count} rows")
    print(f"   - user_activity_logs: {activities_count} rows")
    print(f"   - transactions: {transactions_count} rows")
    
    # 5. Sample data
    print("\n📝 Sample data from users (first 3 rows):")
    sample = conn.execute(text("SELECT * FROM users LIMIT 3"))
    for row in sample:
        print(f"   {row}")

print("\n" + "="*50)