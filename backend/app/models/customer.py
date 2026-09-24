from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from app.db.session import Base


class Customer(Base):
    """A customer/account the AI teammate provides support for."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # "free" | "pro" | "enterprise" — used later by the agent's policy
    # rules to decide how cautious to be (e.g. always escalate enterprise).
    plan = Column(String, nullable=False, default="free")

    # Lifetime value in dollars. Used later for risk-scoring decisions
    # (e.g. be more careful with high-value customers).
    customer_value = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="customer")
