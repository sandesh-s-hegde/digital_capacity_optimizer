import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_table():
    url = os.getenv('DATABASE_URL')
    if not url:
        print("❌ Error: DATABASE_URL not found in .env file.")
        return

    print(f"🌍 Connecting to database...")
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()

        # Create the table structure
        create_query = """
                       CREATE TABLE IF NOT EXISTS inventory \
                       ( \
                           id \
                           SERIAL \
                           PRIMARY \
                           KEY, \
                           date \
                           DATE \
                           NOT \
                           NULL, \
                           product_name \
                           TEXT \
                           NOT \
                           NULL, \
                           demand \
                           INTEGER \
                           NOT \
                           NULL
                       ); \
                       """
        cur.execute(create_query)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ SUCCESS: Table 'inventory' created.")
    except Exception as e:
        print(f"❌ Failed: {e}")


if __name__ == "__main__":
    create_table()