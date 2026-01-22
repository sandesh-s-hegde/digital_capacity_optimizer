import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from database_schema import engine, DemandLog
import config


def load_data(selected_product=None):
    """Fetches records, optionally filtering by Product."""
    try:
        if selected_product:
            # Use parametrized query for safety
            query = text("SELECT * FROM demand_logs_v2 WHERE product_name = :p ORDER BY date ASC")
            df = pd.read_sql(query, engine, params={"p": selected_product})
        else:
            query = text("SELECT * FROM demand_logs_v2 ORDER BY date ASC")
            df = pd.read_sql(query, engine)

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"DB Load Error: {e}")
        return None


def get_unique_products():
    """Fetches unique product names for the dropdown."""
    try:
        query = text("SELECT DISTINCT product_name FROM demand_logs_v2 ORDER BY product_name")
        df = pd.read_sql(query, engine)
        return df['product_name'].tolist() if not df.empty else []
    except:
        return []


def add_record(log_date, product_name, demand_qty):
    """Adds a single record to the database."""
    try:
        with Session(engine) as session:
            new_log = DemandLog(
                date=log_date,
                product_name=product_name,
                demand=demand_qty,
                region="Global",
                unit_price=config.HOLDING_COST
            )
            session.add(new_log)
            session.commit()
            return True
    except Exception as e:
        print(f"Add Error: {e}")
        return False


def delete_record(record_id):
    """Deletes a record by its unique ID."""
    try:
        with Session(engine) as session:
            record = session.get(DemandLog, int(record_id))
            if record:
                session.delete(record)
                session.commit()
                return True
            else:
                return False
    except Exception as e:
        print(f"Delete Error: {e}")
        return False


def bulk_import_csv(df):
    """
    Takes a Pandas DataFrame and bulk inserts it.
    """
    try:
        with Session(engine) as session:
            for index, row in df.iterrows():
                new_log = DemandLog(
                    date=pd.to_datetime(row['date']),
                    product_name=row['product_name'],
                    demand=int(row['demand']),
                    region="Global",
                    unit_price=config.HOLDING_COST
                )
                session.add(new_log)
            session.commit()
            return True, f"Successfully imported {len(df)} records."
    except Exception as e:
        return False, str(e)


def reset_database():
    """
    WARNING: Deletes ALL data and resets ID counter to 1.
    """
    try:
        with Session(engine) as session:
            # TRUNCATE is faster than DELETE and resets the identity column
            session.execute(text("TRUNCATE TABLE demand_logs_v2 RESTART IDENTITY;"))
            session.commit()
            return True
    except Exception as e:
        print(f"Reset Failed: {e}")
        return False