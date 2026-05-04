"""
Database Configuration untuk INDICO Portfolio
Fixed version - compatible with PostgreSQL on macOS
"""

import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd

# Konfigurasi database untuk macOS (Postgres.app)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'indico_db',
    'user': '',  # Kosongkan dulu, akan diisi otomatis
    'password': ''  # Kosong (Postgres.app default no password)
}

def get_connection():
    """Mendapatkan koneksi database - versi yang sudah diperbaiki"""
    
    # Coba beberapa kemungkinan user
    possible_users = ['', 'postgres', 'indico_env']  # '' = current system user
    
    for user in possible_users:
        try:
            # Update config dengan user yang dicoba
            config = DB_CONFIG.copy()
            config['user'] = user if user else None  # None = current user
            
            # Buat koneksi
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'] if config['user'] else None,
                password=config['password'] if config['password'] else None
            )
            print(f"✅ Koneksi berhasil dengan user: '{user if user else '(current user)'}'")
            return conn
        except psycopg2.OperationalError as e:
            if 'does not exist' in str(e):
                print(f"⚠️ Database 'indico_db' belum ada. Buat dulu dengan: createdb indico_db")
                return None
            continue
        except Exception as e:
            continue
    
    print("❌ Gagal koneksi ke database. Pastikan:")
    print("   1. PostgreSQL sudah running (cek: pg_isready)")
    print("   2. Database 'indico_db' sudah dibuat")
    print("   3. Tidak ada firewall blocking port 5432")
    return None

def get_engine():
    """Mendapatkan SQLAlchemy engine - versi yang sudah diperbaiki"""
    try:
        # Coba koneksi dulu untuk dapat user yang benar
        conn = get_connection()
        if conn:
            user = conn.info.user
            conn.close()
            
            # Build URL dengan user yang benar
            url = f"postgresql://{user}@localhost:5432/indico_db"
            return create_engine(url)
    except:
        pass
    
    # Fallback: coba tanpa user specifik
    try:
        url = "postgresql:///indico_db?host=localhost"
        return create_engine(url)
    except:
        print("❌ Gagal membuat engine")
        return None

def test_connection():
    """Test koneksi dengan query sederhana - VERSION YANG SUDAH DIPERBAIKI"""
    try:
        engine = get_engine()
        if engine is None:
            return False
        
        # PENTING: Gunakan text() untuk raw SQL
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Terhubung ke: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Gagal koneksi: {e}")
        return False

def create_database_if_not_exists():
    """Membuat database jika belum ada"""
    try:
        # Koneksi ke database default 'postgres'
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='postgres',
            user='',
            password=''
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Cek apakah database indico_db sudah ada
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'indico_db'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute("CREATE DATABASE indico_db")
            print("✅ Database 'indico_db' berhasil dibuat")
        else:
            print("✅ Database 'indico_db' sudah ada")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Tidak bisa buat database: {e}")
        print("   Silakan buat manual dengan: createdb indico_db")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    print("-" * 40)
    
    # Step 1: Pastikan database ada
    create_database_if_not_exists()
    
    # Step 2: Test koneksi
    print("\n🔌 Mencoba koneksi...")
    test_connection()