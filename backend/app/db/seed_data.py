"""
Seeds the database with realistic demo customers and tickets.

`seed_if_empty` is idempotent: it only inserts data if the customers
table is empty, so it's safe to call on every app startup.
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.ticket import Ticket


def seed_if_empty(db: Session) -> None:
    if db.query(Customer).first() is not None:
        return  # already seeded, nothing to do

    now = datetime.utcnow()

    customers = [
        Customer(
            name="Priya Sharma",
            email="priya.sharma@nimbuscorp.com",
            plan="enterprise",
            customer_value=48000.0,
            created_at=now - timedelta(days=720),
        ),
        Customer(
            name="Daniel Osei",
            email="daniel.osei@brightretail.io",
            plan="pro",
            customer_value=6200.0,
            created_at=now - timedelta(days=340),
        ),
        Customer(
            name="Mei Lin",
            email="mei.lin@fastcart.com",
            plan="free",
            customer_value=0.0,
            created_at=now - timedelta(days=40),
        ),
        Customer(
            name="Carlos Mendez",
            email="carlos.mendez@vertexlogistics.com",
            plan="enterprise",
            customer_value=91500.0,
            created_at=now - timedelta(days=980),
        ),
        Customer(
            name="Aisha Rahman",
            email="aisha.rahman@brewhousecafe.com",
            plan="pro",
            customer_value=3100.0,
            created_at=now - timedelta(days=210),
        ),
        Customer(
            name="Tom Becker",
            email="tom.becker@studiozero.dev",
            plan="free",
            customer_value=0.0,
            created_at=now - timedelta(days=15),
        ),
    ]
    db.add_all(customers)
    db.flush()  # assigns primary key ids without committing yet

    tickets = [
        Ticket(
            customer_id=customers[0].id,
            subject="Unable to export quarterly report",
            message="Our finance team can't export the Q3 report, the export button just spins forever.",
            status="open",
            priority="high",
            created_at=now - timedelta(hours=3),
        ),
        Ticket(
            customer_id=customers[0].id,
            subject="Request to cancel add-on seats",
            message="We'd like to remove 5 seats from our enterprise plan starting next billing cycle.",
            status="open",
            priority="urgent",
            created_at=now - timedelta(hours=1),
        ),
        Ticket(
            customer_id=customers[1].id,
            subject="Refund request for duplicate charge",
            message="I was charged twice for my August subscription. Please refund one of the charges.",
            status="open",
            priority="normal",
            created_at=now - timedelta(hours=6),
        ),
        Ticket(
            customer_id=customers[2].id,
            subject="How do I upgrade my plan?",
            message="I want to move from the free plan to Pro. What are the steps?",
            status="open",
            priority="low",
            created_at=now - timedelta(hours=20),
        ),
        Ticket(
            customer_id=customers[3].id,
            subject="API integration returning 500 errors",
            message="Our production integration has been failing intermittently since this morning. This is affecting live orders.",
            status="open",
            priority="urgent",
            created_at=now - timedelta(minutes=45),
        ),
        Ticket(
            customer_id=customers[4].id,
            subject="Question about invoice line items",
            message="Can you clarify what the 'platform fee' line item on our latest invoice covers?",
            status="open",
            priority="normal",
            created_at=now - timedelta(hours=10),
        ),
        Ticket(
            customer_id=customers[5].id,
            subject="Trouble resetting password",
            message="The password reset email never arrives, I've checked spam too.",
            status="open",
            priority="normal",
            created_at=now - timedelta(hours=2),
        ),
        Ticket(
            customer_id=customers[1].id,
            subject="Feature request: bulk CSV import",
            message="Would love to bulk import contacts via CSV instead of adding them one by one.",
            status="open",
            priority="low",
            created_at=now - timedelta(days=2),
        ),
    ]
    db.add_all(tickets)
    db.commit()
