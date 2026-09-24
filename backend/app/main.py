"""
FastAPI entrypoint.

Milestone 1 scope only:
- App startup creates tables and seeds demo data.
- GET /tickets returns all tickets with their related customer info.

No AI agent, no frontend — that comes in later milestones.
"""

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db, init_db, SessionLocal
from app.db.seed_data import seed_if_empty
from app.models.ticket import Ticket


# ---- Response schemas -------------------------------------------------
# Small, local Pydantic models just for shaping the /tickets response.
# Kept in main.py for now since this is the only endpoint; if the API
# grows, these should move into their own schemas.py.

class CustomerSummary(BaseModel):
    id: int
    name: str
    email: str
    plan: str
    customer_value: float

    class Config:
        from_attributes = True  # allows building this from an ORM object


class TicketOut(BaseModel):
    id: int
    subject: str
    message: str
    status: str
    priority: str
    created_at: datetime
    customer: CustomerSummary

    class Config:
        from_attributes = True


# ---- App setup ----------------------------------------------------------

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables and seed demo data if the DB is empty."""
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "service": settings.APP_NAME}


@app.get("/tickets", response_model=List[TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    """Return all tickets, newest first, with basic customer info attached."""
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    return tickets
