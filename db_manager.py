import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime


# --- DATABASE CONNECTION ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database with SSL fallback."""
    url = os.getenv('DATABASE_URL')
    if not url:
        return None

    try:
        # Standard connection
        conn = psycopg2.connect(url)
        return conn
    except Exception:
        try:
            # Fallback for local-to-cloud connections requiring SSL
            conn = psycopg2.connect(url, sslmode='require')
            return conn
        except Exception as e:
            print(f"❌ DB Connection Error: {e}")
            return None


# --- INITIALIZE DATABASE ---
def init_db():
    """
    Initializes the database schema.
    Ensures the 'inventory' table exists on the new Render instance.
    """
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Standardizing table for v4.0.0 Research Artifact
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    product_name VARCHAR(255) NOT NULL,
                    demand FLOAT DEFAULT 0,
                    avg_demand FLOAT DEFAULT 0,
                    std_dev FLOAT DEFAULT 0,
                    lead_time FLOAT DEFAULT 0,
                    service_level FLOAT DEFAULT 0.95
                );
            """)
            conn.commit()
            cur.close()
            print("✅ Database Schema Verified.")
        except Exception as e:
            print(f"❌ Schema Initialization Error: {e}")
        finally:
            conn.close()


# --- LOAD DATA ---
def load_data(product_name=None):
    """Loads inventory data into a DataFrame."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        query = "SELECT * FROM inventory"
        params = ()

        if product_name:
            query += " WHERE product_name = %s"
            params = (product_name,)

        query += " ORDER BY date ASC;"
        df = pd.read_sql(query, conn, params=params)

        if not df.empty and 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        return df
    except Exception as e:
        print(f"❌ Load Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()


# --- ADD SINGLE RECORD ---
def add_record(date_val, product, demand):
    """Inserts a single transaction into the database."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)",
            (date_val, product, demand)
        )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Add Error: {e}")
        return False
    finally:
        conn.close()


# --- BULK IMPORT ---
def bulk_import_csv(df):
    """Efficiently uploads a pandas DataFrame to the database."""
    conn = get_db_connection()
    if not conn:
        return False, "No Database Connection"

    try:
        cur = conn.cursor()
        # Ensure we only try to import columns that exist in the CSV
        cols = ['date', 'product_name', 'demand']
        data_tuples = [tuple(x) for x in df[cols].to_numpy()]

        query = "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)"
        cur.executemany(query, data_tuples)

        conn.commit()
        cur.close()
        return True, f"Successfully imported {len(df)} records."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# --- GET UNIQUE PRODUCTS ---
def get_unique_products():
    """Returns a list of unique product names for selection UI."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT product_name FROM inventory ORDER BY product_name;")
        rows = cur.fetchall()
        cur.close()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"❌ Filter Error: {e}")
        return []
    finally:
        conn.close()


# --- RESET DATABASE ---
def reset_database():
    """Wipes all data while keeping the schema intact."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY;")
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Reset Error: {e}")
        return False
    finally:
        conn.close()


# --- DELETE SPECIFIC RECORD ---
def delete_record(record_id):
    """Deletes a specific record by ID."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE id = %s;", (record_id,))
            conn.commit()
            cursor.close()
            return True, "Record deleted."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection failed."
