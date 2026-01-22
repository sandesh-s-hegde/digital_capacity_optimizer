from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()


class DemandLog(Base):
    """
    Table Definition: demand_logs_v2
    Includes 'product_name' to support Multi-SKU management.
    """
    __tablename__ = 'demand_logs_v2'  # <--- New Table Name

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    product_name = Column(String, nullable=False, default="Generic")  # <--- NEW COLUMN
    demand = Column(Integer, nullable=False)
    region = Column(String, default="Global")
    unit_price = Column(Float, default=0.0)


# Connect to Database
db_connection_string = os.getenv("DATABASE_URL")

# Fix for Render's postgres connection string requirement
if db_connection_string and db_connection_string.startswith("postgres://"):
    db_connection_string = db_connection_string.replace("postgres://", "postgresql://", 1)

if db_connection_string:
    engine = create_engine(db_connection_string, echo=False)
    Base.metadata.create_all(engine)  # Creates the table if it doesn't exist
else:
    print("⚠️ Warning: DATABASE_URL not found.")
    engine = None