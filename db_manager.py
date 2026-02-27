import os
import logging
import psycopg2
import pandas as pd

# Configure enterprise-grade logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database with SSL fallback."""
    url = os.getenv('DATABASE_URL')
    if not url:
        return None

    try:
        return psycopg2.connect(url)
    except psycopg2.OperationalError:
        try:
            return psycopg2.connect(url, sslmode='require')
        except Exception as e:
            logger.error("Database connection failed: %s", e)
            return None

def init_db():
    """Initializes the required database schema."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cur:
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
    except Exception as e:
        logger.error("Schema initialization error: %s", e)
    finally:
        conn.close()

def load_data(product_name=None):
    """Loads inventory data into a Pandas DataFrame."""
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
        logger.error("Data load error: %s", e)
        return pd.DataFrame()
    finally:
        conn.close()

def add_record(date_val, product, demand):
    """Inserts a single transaction into the database."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)",
                (date_val, product, demand)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error("Add record error: %s", e)
        return False
    finally:
        conn.close()

def bulk_import_csv(df):
    """Efficiently uploads a pandas DataFrame to the database."""
    conn = get_db_connection()
    if not conn:
        return False, "No database connection."

    try:
        with conn.cursor() as cur:
            cols = ['date', 'product_name', 'demand']
            data_tuples = [tuple(x) for x in df[cols].to_numpy()]

            query = "INSERT INTO inventory (date, product_name, demand) VALUES (%s, %s, %s)"
            cur.executemany(query, data_tuples)
            conn.commit()
        return True, f"Successfully imported {len(df)} records."
    except Exception as e:
        logger.error("Bulk import error: %s", e)
        return False, str(e)
    finally:
        conn.close()

def get_unique_products():
    """Returns a list of unique product names."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT product_name FROM inventory ORDER BY product_name;")
            rows = cur.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        logger.error("Fetch unique products error: %s", e)
        return []
    finally:
        conn.close()

def reset_database():
    """Truncates the inventory table, resetting all data."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE inventory RESTART IDENTITY;")
            conn.commit()
        return True
    except Exception as e:
        logger.error("Database reset error: %s", e)
        return False
    finally:
        conn.close()

def delete_record(record_id):
    """Deletes a specific record by ID."""
    conn = get_db_connection()
    if not conn:
        return False, "Connection failed."

    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM inventory WHERE id = %s;", (record_id,))
            conn.commit()
        return True, "Record deleted."
    except Exception as e:
        logger.error("Delete record error: %s", e)
        return False, str(e)
    finally:
        conn.close()
