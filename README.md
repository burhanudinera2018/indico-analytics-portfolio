# INDICO Digital Ecosystem Analytics Portfolio Project

## 🎯 Project Overview
Data Analytics portfolio project simulating real-world challenges at **INDICO** (Telkomsel's digital subsidiary), analyzing user engagement and business performance across three digital products:
- **Kuncie** (Edu-tech)
- **Fita** (Health-tech)  
- **Majamojo** (Game Publishing)

## 🛠️ Tech Stack
- **Database**: PostgreSQL 15
- **Analytics**: Python 3.11.11, Pandas, NumPy
- **Visualization**: Streamlit, Plotly, Matplotlib
- **Data Generation**: Faker library

## 📊 Key Analyses Performed

### 1. Retention Cohort Analysis
- Monthly retention tracking per business unit
- Identified Kuncie has loyal user base (45% D30 retention)
- Majamojo needs retention strategy (only 28% D30)

### 2. Cross-Product Engagement
- Only 8% users use multiple products → Rp 2.1B cross-sell opportunity
- Recommended bundle discount for game → edutech users

### 3. Customer Lifetime Value (LTV)
- Kuncie: Rp 250k/user/month (highest)
- Majamojo: Rp 85k/user/month but largest volume
- Strategy to convert game users to subscription model

### 4. Feature Performance
- "Live Class" drives 40% of Kuncie revenue
- "Battle Mode" highest engagement but low conversion in Majamojo

## 🚀 How to Run This Project

### Prerequisites
```bash
Python 3.11.11
PostgreSQL 15
Docker (optional)