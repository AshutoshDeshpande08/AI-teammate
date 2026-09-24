"""
Context Builder.

Given a ticket ID, this module loads the ticket and its related customer
from the database and packages everything the agent will need into a
single, structured object: a `TicketContext`.

This is intentionally "dumb" — no LLM calls, no decisions, no tools.
It only answers the question: "what does the agent need to know before
it can reason about this ticket?"
"""

from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class TicketNotFoundError(Exception):
    """Raised when a context is requested for a ticket ID that doesn't exist."""

    def __init__(self, ticket_id: int):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket with id={ticket_id} was not found.")


class TicketContext(BaseModel):
    """Everything the agent needs to know about one ticket, in one place."""

    ticket_id: int
    customer_id: int
    customer_name: str
    customer_email: str
    customer_plan: str
    customer_value: float
    ticket_subject: str
    ticket_message: str
    ticket_status: str
    ticket_priority: str
    ticket_created_at: datetime


def build_ticket_context(ticket_id: int, db: Session) -> TicketContext:
    """Load a ticket and its customer, and return them as a TicketContext.

    Raises:
        TicketNotFoundError: if no ticket with `ticket_id` exists.
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if ticket is None:
        raise TicketNotFoundError(ticket_id)

    customer = ticket.customer  # loaded via the existing relationship

    return TicketContext(
        ticket_id=ticket.id,
        customer_id=customer.id,
        customer_name=customer.name,
        customer_email=customer.email,
        customer_plan=customer.plan,
        customer_value=customer.customer_value,
        ticket_subject=ticket.subject,
        ticket_message=ticket.message,
        ticket_status=ticket.status,
        ticket_priority=ticket.priority,
        ticket_created_at=ticket.created_at,
    )