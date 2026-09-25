"""
FastAPI entrypoint.

Current scope:
- App startup creates tables and seeds demo data.
- GET /tickets returns all tickets with customer information.
- POST /tickets/{ticket_id}/analyze runs the real AI pipeline.
- POST /tickets/{ticket_id}/escalate executes the escalation action.
"""

from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db, init_db, SessionLocal
from app.db.seed_data import seed_if_empty
from app.models.ticket import Ticket

from app.agent.context_builder import (
    build_ticket_context,
    TicketNotFoundError,
)
from app.agent.decision_engine import (
    decide_ticket,
    DecisionEngineError,
)
from app.agent.risk_scorer import assess_risk

from app.tools.ticket_tool import update_ticket_status


# ---- Response schemas -------------------------------------------------


class CustomerSummary(BaseModel):
    id: int
    name: str
    email: str
    plan: str
    customer_value: float

    class Config:
        from_attributes = True


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


class ActionResponse(BaseModel):
    success: bool
    ticket_id: int
    action: str
    status: str
    message: str


class AnalysisResponse(BaseModel):
    decision: dict
    risk: dict


# ---- App setup --------------------------------------------------------


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


# ---- CORS -------------------------------------------------------------


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Startup ----------------------------------------------------------


@app.on_event("startup")
def on_startup() -> None:
    """Create tables and seed demo data."""

    init_db()

    db = SessionLocal()

    try:
        seed_if_empty(db)
    finally:
        db.close()


# ---- Basic endpoints --------------------------------------------------


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }


@app.get("/tickets", response_model=List[TicketOut])
def list_tickets(db: Session = Depends(get_db)):
    """Return all tickets with customer information."""

    tickets = (
        db.query(Ticket)
        .order_by(Ticket.created_at.desc())
        .all()
    )

    return tickets


# ---- AI analysis endpoint --------------------------------------------


@app.post(
    "/tickets/{ticket_id}/analyze",
    response_model=AnalysisResponse,
)
def analyze_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Run the AI teammate reasoning pipeline for one ticket.

    Pipeline:

    Ticket
        ↓
    Context Builder
        ↓
    Gemini Decision Engine
        ↓
    Risk / Autonomy Gate

    No customer-facing or database-changing action happens here.
    """

    try:
        # 1. Build the complete context for the ticket.
        context = build_ticket_context(
            ticket_id=ticket_id,
            db=db,
        )

        # 2. Ask Gemini to reason about the ticket.
        decision = decide_ticket(context)

        # 3. Apply deterministic safety rules.
        risk = assess_risk(decision)

        return AnalysisResponse(
            decision=decision.model_dump(mode="json"),
            risk=risk.model_dump(mode="json"),
        )

    except TicketNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket #{ticket_id} was not found.",
        )

    except DecisionEngineError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )


# ---- Action endpoints ------------------------------------------------


@app.post(
    "/tickets/{ticket_id}/escalate",
    response_model=ActionResponse,
)
def escalate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Escalate a ticket to a human support agent.

    The actual database change is performed through
    the existing ticket tool.
    """

    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket #{ticket_id} was not found.",
        )

    result = update_ticket_status(
        ticket_id=ticket_id,
        status="escalated",
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.message,
        )

    return ActionResponse(
        success=True,
        ticket_id=ticket_id,
        action="escalate_to_human",
        status="escalated",
        message=result.message,
    )