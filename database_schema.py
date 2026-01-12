"""
database_schema.py
Defines the SQL structure using SQLAlchemy ORM.
Designed to be compatible with SQLite (Dev) and PostgreSQL (Prod).
"""
from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.orm import declarative_base

# 1. Define the Database Connection
# FOR NOW: We use SQLite for local development
DATABASE_URL = "sqlite:///inventory_system.db"

# FUTURE: Uncomment this for PostgreSQL
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# 2. Define the Table Structure
class DemandLog(Base):
    __tablename__ = 'demand_logs'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    region = Column(String, default="Global")
    demand = Column(Integer, nullable=False)

    # Financial context for this specific record (optional)
    unit_price = Column(Float, default=0.0)

# 3. Create the Database
def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database initialized: inventory_system.db")

if __name__ == "__main__":
    init_db()