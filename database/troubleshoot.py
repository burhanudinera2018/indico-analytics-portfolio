"""
Troubleshooting tools untuk database
"""

import psycopg2
from db_config import DB_CONFIG

def check_postgres_running():
    """Cek apakah PostgreSQL service sedang running"""
    import subprocess
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        try:
            result = subprocess.run(['sc', 'query', 'postgresql-x64-15'], 
                                  capture_output=True, text=True)
            if "RUNNING" in result.stdout:
                print("✅ PostgreSQL service is RUNNING")
                return True
            else:
                print("❌ PostgreSQL service is STOPPED")
                return False
        except:
            print("⚠️  Tidak bisa cek service. Coba manual di Services.msc")
            return None
    
    elif system in ["Linux", "Darwin"]:  # Darwn = Mac
        try:
            result = subprocess.run(['pg_isready'], capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("✅ PostgreSQL is RUNNING")
                return True
            else:
                print("❌ PostgreSQL is NOT running")
                return False
        except:
            print("⚠️  Tidak bisa cek. Coba: sudo systemctl status postgresql")
            return None

def test_manual_connection():
    """Test koneksi manual dengan berbagai parameter"""
    
    print("\n🔌 Testing koneksi dengan berbagai config...")
    
    # Test dengan host yang berbeda
    hosts = ['localhost', '127.0.0.1', '0.0.0.0']
    
    for host in hosts:
        try:
            conn = psycopg2.connect(
                host=host,
                port=5432,
                database='postgres',  # coba database default
                user='postgres',
                password='indico123'
            )
            print(f"   ✅ Connect successful with host={host}")
            conn.close()
            return True
        except Exception as e:
            print(f"   ❌ Failed with host={host}: {str(e)[:50]}")
    
    return False

def show_connection_info():
    """Menampilkan informasi koneksi yang benar"""
    
    print("\n📋 Informasi koneksi yang benar:")
    print("   Host: localhost atau 127.0.0.1")
    print("   Port: 5432")
    print("   Database: indico_db (atau postgres untuk test)")
    print("   User: postgres")
    print("   Password: [password yang Anda buat saat install]")
    print("\n💡 Tips:")
    print("   1. Pastikan PostgreSQL service running")
    print("   2. Cek firewall tidak memblock port 5432")
    print("   3. Coba restart PostgreSQL service")

if __name__ == "__main__":
    print("="*50)
    print("Database Troubleshooting Tool")
    print("="*50)
    
    check_postgres_running()
    test_manual_connection()
    show_connection_info()