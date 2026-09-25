from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.ticket import Ticket


class TicketActionResult(BaseModel):
    success: bool
    ticket_id: int
    action: str
    message: str


def update_ticket_status(
    ticket_id: int,
    status: str,
) -> TicketActionResult:
    """Update a ticket's status in the database."""

    db: Session = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if ticket is None:
            return TicketActionResult(
                success=False,
                ticket_id=ticket_id,
                action="update_ticket_status",
                message=f"Ticket #{ticket_id} was not found.",
            )

        ticket.status = status
        db.commit()

        return TicketActionResult(
            success=True,
            ticket_id=ticket_id,
            action="update_ticket_status",
            message=f"Ticket #{ticket_id} status updated to '{status}'.",
        )

    finally:
        db.close()