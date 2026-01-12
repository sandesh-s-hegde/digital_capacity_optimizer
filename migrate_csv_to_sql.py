"""
migrate_csv_to_sql.py
Robust script to load CSV data into SQLite.
Handles numeric indices AND English month names (Jan, Feb...).
"""
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database_schema import engine, DemandLog, init_db
from datetime import datetime, date
import os

def migrate_data(csv_path="mock_data.csv"):
    # 1. Initialize DB
    init_db()

    # 2. Load CSV
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return

    print(f"Reading {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # 3. Clean Column Names
    df.columns = df.columns.str.strip().str.lower()

    # Map 'month' or 'date' to our internal variable
    if 'date' in df.columns:
        date_col = 'date'
    elif 'month' in df.columns:
        date_col = 'month'
    else:
        print(f"❌ Error: Columns not found. Found: {df.columns.tolist()}")
        return

    # 4. Connect to SQL
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(DemandLog).count() > 0:
        print("⚠️ Database already has data. Skipping migration.")
        session.close()
        return

    # 5. Migrate Data
    print("Migrating data...")
    count = 0

    # Mapping for English Month Names
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    # Base year for reconstruction (Assuming 2024 for the mock data)
    BASE_YEAR = 2024

    for _, row in df.iterrows():
        try:
            raw_val = str(row[date_col]).strip()

            # ATTEMPT 1: Is it a full date? (e.g. "2024-01-01")
            try:
                date_obj = pd.to_datetime(raw_val).date()
            except:
                # ATTEMPT 2: Is it a Month Name? (e.g. "Jan", "Feb")
                clean_month = raw_val[:3].lower() # Take first 3 chars
                if clean_month in month_map:
                    month_num = month_map[clean_month]
                    date_obj = date(BASE_YEAR, month_num, 1) # Create 2024-01-01
                else:
                    # ATTEMPT 3: Is it a number? (e.g. 0, 1)
                    month_offset = int(float(raw_val))
                    # Fallback to relative calculation
                    from datetime import timedelta
                    base = date(BASE_YEAR, 1, 1)
                    date_obj = base + timedelta(days=month_offset*30)

            log = DemandLog(
                date=date_obj,
                demand=int(row['demand'])
            )
            session.add(log)
            count += 1
        except Exception as e:
            print(f"⚠️ Skipping row '{raw_val}': {e}")

    session.commit()
    print(f"✅ Success! Moved {count} records to SQL.")
    session.close()

if __name__ == "__main__":
    migrate_data()