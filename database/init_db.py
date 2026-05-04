import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'indico_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'indico123')
}

def get_connection():
    return psycopg2.connect(**DB_PARAMS)

def get_engine():
    url = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['database']}"
    return create_engine(url)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    
    # Create users table
    cur.execute("""
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
    """)
    
    # Create user_activity_logs table
    cur.execute("""
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
    """)
    
    # Create transactions table
    cur.execute("""
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
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created successfully")

def insert_data_from_csv():
    engine = get_engine()
    
    # Insert users
    users_df = pd.read_csv('data/users.csv')
    users_df.to_sql('users', engine, if_exists='append', index=False)
    print(f"✅ Inserted {len(users_df)} users")
    
    # Insert activity logs
    activities_df = pd.read_csv('data/user_activity_logs.csv')
    activities_df.to_sql('user_activity_logs', engine, if_exists='append', index=False)
    print(f"✅ Inserted {len(activities_df)} activity logs")
    
    # Insert transactions
    transactions_df = pd.read_csv('data/transactions.csv')
    transactions_df.to_sql('transactions', engine, if_exists='append', index=False)
    print(f"✅ Inserted {len(transactions_df)} transactions")

if __name__ == "__main__":
    create_tables()
    insert_data_from_csv()
    print("\n🎉 Database setup complete!")