"""
FINAL SCRIPT - Generate Dataset untuk INDICO Portfolio
Langsung jalan, langsung dapat 500+ users dengan distribusi realistis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

print("🚀 Starting dataset generation for INDICO portfolio...")

# KONFIGURASI
NUM_USERS = 500
DAYS_OF_ACTIVITY = 60
START_DATE = datetime(2024, 1, 1)

BUSINESS_UNITS = ['Kuncie', 'Fita', 'Majamojo']
CITIES = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Semarang', 'Makassar']
DEVICE_TYPES = ['Mobile', 'Desktop']
AGE_GROUPS = ['18-24', '25-34', '35-44', '45+']
GENDERS = ['Male', 'Female']

FEATURES = {
    'Kuncie': ['Video Pembelajaran', 'Kuis Interaktif', 'Live Class', 'Download Materi', 'Forum Diskusi'],
    'Fita': ['Cek Kesehatan', 'Artikel Kesehatan', 'Reservasi Dokter', 'Konsultasi Online', 'Tracking Olahraga'],
    'Majamojo': ['Battle Mode', 'Event Mingguan', 'Clan War', 'Shop Item', 'Daily Reward']
}

# 1. GENERATE USERS
print("📝 Generating users...")
users = []
for i in range(1, NUM_USERS + 1):
    reg_date = START_DATE + timedelta(days=random.randint(0, 45))
    
    # Weighted distribution untuk business_unit (simulasi popularitas)
    business_unit = random.choices(
        BUSINESS_UNITS, 
        weights=[0.35, 0.30, 0.35],  # Kuncie & Majamojo lebih populer
        k=1
    )[0]
    
    user = {
        'user_id': f'U{str(i).zfill(4)}',
        'business_unit': business_unit,
        'registration_date': reg_date.strftime('%Y-%m-%d'),
        'city': random.choice(CITIES),
        'device_type': random.choices(DEVICE_TYPES, weights=[0.75, 0.25])[0],
        'gender': random.choice(GENDERS),
        'age_group': random.choices(AGE_GROUPS, weights=[0.25, 0.40, 0.25, 0.10])[0]
    }
    users.append(user)

df_users = pd.DataFrame(users)
print(f"   ✅ Generated {len(df_users)} users")

# 2. GENERATE ACTIVITY LOGS
print("📝 Generating activity logs...")
logs = []
log_id = 1

for _, user in df_users.iterrows():
    user_id = user['user_id']
    business_unit = user['business_unit']
    reg_date = datetime.strptime(user['registration_date'], '%Y-%m-%d')
    
    # Jumlah aktivitas: antara 5-30 kali dalam periode
    num_activities = random.randint(5, 30)
    
    for _ in range(num_activities):
        # Aktivitas terjadi 1-60 hari setelah registrasi
        days_after_reg = random.randint(1, DAYS_OF_ACTIVITY)
        activity_date = reg_date + timedelta(days=days_after_reg)
        
        if activity_date > datetime.now():
            continue
            
        # Session duration: normal distribution 45 menit, std 15
        session_min = int(np.random.normal(45, 15))
        session_min = max(5, min(180, session_min))
        
        # Random feature
        feature_used = random.choice(FEATURES[business_unit])
        
        # Probabilitas transaksi: 30%
        has_transaction = random.random() < 0.3
        transaction_amt = 0
        if has_transaction:
            if business_unit == 'Kuncie':
                transaction_amt = random.choice([150000, 200000, 250000, 300000])
            elif business_unit == 'Fita':
                transaction_amt = random.choice([75000, 150000, 200000, 250000])
            else:
                transaction_amt = random.choice([50000, 75000, 100000, 150000, 200000])
        
        log = {
            'log_id': f'L{str(log_id).zfill(6)}',
            'user_id': user_id,
            'activity_date': activity_date.strftime('%Y-%m-%d'),
            'business_unit': business_unit,
            'session_duration_min': session_min,
            'feature_used': feature_used,
            'transaction_amt': transaction_amt
        }
        logs.append(log)
        log_id += 1

df_activities = pd.DataFrame(logs)
print(f"   ✅ Generated {len(df_activities)} activity logs")

# 3. GENERATE TRANSACTIONS (dari logs yang ada transaksi)
print("📝 Generating transactions...")
transactions = []
trans_id = 1

activities_with_transaction = df_activities[df_activities['transaction_amt'] > 0]

for _, act in activities_with_transaction.iterrows():
    payment_method = random.choices(
        ['Mobile Wallet', 'Card', 'Bank Transfer'], 
        weights=[0.55, 0.30, 0.15]
    )[0]
    
    # Subscription type berdasarkan business unit
    if act['business_unit'] == 'Kuncie':
        sub_type = random.choices(['Bulanan', 'Tahunan'], weights=[0.7, 0.3])[0]
    elif act['business_unit'] == 'Fita':
        sub_type = random.choices(['Sesi Konsultasi', 'Paket Bulanan', 'Paket Tahunan'], weights=[0.5, 0.4, 0.1])[0]
    else:
        sub_type = random.choices(['Item Game', 'Bulanan', 'Paket Event'], weights=[0.6, 0.3, 0.1])[0]
    
    transaction = {
        'transaction_id': f'TRX{str(trans_id).zfill(6)}',
        'user_id': act['user_id'],
        'business_unit': act['business_unit'],
        'transaction_date': act['activity_date'],
        'amount': act['transaction_amt'],
        'payment_method': payment_method,
        'subscription_type': sub_type
    }
    transactions.append(transaction)
    trans_id += 1

df_transactions = pd.DataFrame(transactions)
print(f"   ✅ Generated {len(df_transactions)} transactions")

# 4. SAVE TO CSV
print("💾 Saving datasets...")
df_users.to_csv('data/users.csv', index=False)
df_activities.to_csv('data/user_activity_logs.csv', index=False)
df_transactions.to_csv('data/transactions.csv', index=False)

# 5. STATISTIK RINGKASAN
print("\n" + "="*50)
print("📊 DATASET GENERATION COMPLETE!")
print("="*50)
print(f"Users:          {len(df_users):,} rows")
print(f"Activity Logs:  {len(df_activities):,} rows")
print(f"Transactions:   {len(df_transactions):,} rows")
print(f"Conversion Rate: {len(df_transactions)/len(df_activities)*100:.1f}%")
print("\nDistribusi Business Unit:")
print(df_users['business_unit'].value_counts())
print("\nDistribusi Age Group:")
print(df_users['age_group'].value_counts())
print("\n✅ Siap untuk lanjut ke PostgreSQL & Streamlit!")

# Optional: Tampilkan sample
print("\n📋 Sample data (users):")
print(df_users.head(3))