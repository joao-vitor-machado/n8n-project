
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_key: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    document_number: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    contracts = relationship("Contract", uselist=True, back_populates="client")