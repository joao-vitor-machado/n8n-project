from datetime import date
from decimal import Decimal

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.database import Base


class ConsumptionReading(Base):
    __tablename__ = "consumption_reading"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reading_key = Column(String(36), unique=True, nullable=False)
    contract_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    reading_date = Column(Date, nullable=False)
    reading_value = Column(Numeric(10, 2), nullable=False)

    contract = relationship("Contract", back_populates="readings")
