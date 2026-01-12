"""
migrate_csv_to_sql.py
One-time script to load CSV data into the database.
"""
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database_schema import engine, DemandLog, init_db
from datetime import datetime
import os


def migrate_data(csv_path="mock_data.csv"):
    # 1. Initialize DB
    init_db()

    # 2. Load CSV
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return

    print(f"Reading {csv_path}...")
    df = pd.read_csv(csv_path)

    # 3. Connect to SQL
    Session = sessionmaker(bind=engine)
    session = Session()

    # 4. Check if data already exists to prevent duplicates
    existing_count = session.query(DemandLog).count()
    if existing_count > 0:
        print(f"⚠️  Database already has {existing_count} records. Skipping migration.")
        session.close()
        return

    # 5. Loop through rows and save to DB
    print("Migrating data...")
    count = 0
    for _, row in df.iterrows():
        try:
            # Handle date format flexibility
            date_str = str(row['Date'])
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()

            log = DemandLog(
                date=date_obj,
                demand=row['Demand']
            )
            session.add(log)
            count += 1
        except Exception as e:
            print(f"⚠️ Skipping row: {e}")

    # 6. Commit Transaction
    session.commit()
    print(f"✅ Success! Moved {count} records to SQL.")
    session.close()


if __name__ == "__main__":
    migrate_data()