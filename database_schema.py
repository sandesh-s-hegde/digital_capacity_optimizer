import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base

load_dotenv()

Base = declarative_base()

class DemandLog(Base):
    __tablename__ = 'demand_logs_v2'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    product_name = Column(String, nullable=False, default="Generic")
    demand = Column(Integer, nullable=False)
    region = Column(String, default="Global")
    unit_price = Column(Float, default=0.0)

db_url = os.getenv("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if db_url:
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
else:
    engine = None
