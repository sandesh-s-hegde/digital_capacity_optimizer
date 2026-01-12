"""
database_schema.py
Defines the SQL structure using SQLAlchemy 2.0 ORM.
"""
from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.orm import DeclarativeBase

# 1. Define the Database Connection
DATABASE_URL = "sqlite:///inventory_system.db"

engine = create_engine(DATABASE_URL)

# 2. Modern Base Class (SQLAlchemy 2.0 Standard)
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

# 4. Create the Database
def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database initialized: inventory_system.db")

if __name__ == "__main__":
    init_db()