from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Ticket(Base):
    """A single support ticket raised by a customer."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)

    # "open" | "pending_approval" | "resolved" | "escalated"
    status = Column(String, nullable=False, default="open")

    # "low" | "normal" | "high" | "urgent"
    priority = Column(String, nullable=False, default="normal")

    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="tickets")
