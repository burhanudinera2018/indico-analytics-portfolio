"""
Membuat tabel-tabel yang diperlukan untuk project INDICO
"""

import psycopg2
from db_config import DB_CONFIG, test_connection

def create_tables():
    """Membuat semua tabel di database"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # SQL statements untuk membuat tabel
    create_table_queries = [
        """
        DROP TABLE IF EXISTS users CASCADE;
        CREATE TABLE users (
            user_id VARCHAR(10) PRIMARY KEY,
            business_unit VARCHAR(20),
            registration_date DATE,
            city VARCHAR(50),
            device_type VARCHAR(10),
            gender VARCHAR(10),
            age_group VARCHAR(10)
        )
        """,
        
        """
        DROP TABLE IF EXISTS user_activity_logs CASCADE;
        CREATE TABLE user_activity_logs (
            log_id VARCHAR(10) PRIMARY KEY,
            user_id VARCHAR(10) REFERENCES users(user_id),
            activity_date DATE,
            business_unit VARCHAR(20),
            session_duration_min INT,
            feature_used VARCHAR(50),
            transaction_amt BIGINT
        )
        """,
        
        """
        DROP TABLE IF EXISTS transactions CASCADE;
        CREATE TABLE transactions (
            transaction_id VARCHAR(10) PRIMARY KEY,
            user_id VARCHAR(10) REFERENCES users(user_id),
            business_unit VARCHAR(20),
            transaction_date DATE,
            amount BIGINT,
            payment_method VARCHAR(20),
            subscription_type VARCHAR(30)
        )
        """
    ]
    
    # Eksekusi setiap query
    for query in create_table_queries:
        try:
            cur.execute(query)
            print(f"✅ Table created: {query.split()[6] if 'DROP' in query else query.split()[2]}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n🎉 Semua tabel berhasil dibuat!")

def show_tables():
    """Menampilkan daftar tabel yang ada"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    print("\n📋 Daftar tabel di database indico_db:")
    for table in tables:
        print(f"   - {table[0]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("="*50)
    print("Setup Database untuk INDICO Portfolio")
    print("="*50)
    
    # Test koneksi dulu
    if test_connection():
        print("\n🔨 Membuat tabel...")
        create_tables()
        show_tables()
    else:
        print("\n❌ Tidak bisa lanjut. Cek konfigurasi database Anda.")
        print("\nTips troubleshooting:")
        print("1. Apakah PostgreSQL sudah running?")
        print("2. Apakah password di DB_CONFIG sesuai?")
        print("3. Coba restart PostgreSQL service")