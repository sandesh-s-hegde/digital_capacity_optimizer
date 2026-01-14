"""
database_schema.py
Defines the SQL structure using SQLAlchemy 2.0 ORM.
"""
import os
from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.orm import DeclarativeBase

# 1. SMART DATABASE CONNECTION
# We check if the cloud has provided a database URL.
# If not, we fall back to local SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///inventory_system.db")

# FIX: SQLAlchemy requires the URL to start with 'postgresql://'
# Render sometimes gives 'postgres://', which crashes newer SQLAlchemy versions.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

# 2. Modern Base Class
class Base(DeclarativeBase):
    pass

# 3. Define the Table Structure
class DemandLog(Base):
    __tablename__ = 'demand_logs'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    region = Column(String, default="Global")
    demand = Column(Integer, nullable=False)
    unit_price = Column(Float, default=0.0)

# 4. Create Tables (Safe to run multiple times)
def init_db():
    Base.metadata.create_all(engine)
    print(f"✅ Database connected: {engine.url.drivername}")

if __name__ == "__main__":
    init_db()