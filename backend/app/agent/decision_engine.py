"""
Decision Engine (structure only — no LLM logic yet).

This module defines what a "decision" looks like: given a TicketContext,
the agent must eventually produce a structured Decision describing what
it thinks should happen with the ticket.

For this milestone, only the shape is defined:
- The Decision model itself, with constrained fields (enums).
- A `decide_ticket` function stub with the final signature, so the rest
  of the app (API layer, tests) can be built against a stable interface
  before the actual reasoning is implemented.

No LLM calls, no tools, no risk scoring — that comes in a later milestone.
"""

from enum import Enum

from pydantic import BaseModel

from app.agent.context_builder import TicketContext


class Intent(str, Enum):
    """What the customer is actually trying to accomplish."""

    BILLING_QUESTION = "billing_question"
    REFUND_REQUEST = "refund_request"
    TECHNICAL_ISSUE = "technical_issue"
    ACCOUNT_CHANGE = "account_change"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    GENERAL_INQUIRY = "general_inquiry"
    OTHER = "other"


class Urgency(str, Enum):
    """How quickly this ticket needs attention."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RecommendedAction(str, Enum):
    """The concrete next step the agent proposes."""

    AUTO_RESOLVE = "auto_resolve"           # answer/resolve directly, no approval needed
    REPLY_TO_CUSTOMER = "reply_to_customer"  # send an informational reply
    ISSUE_REFUND = "issue_refund"           # requires the refund tool (later milestone)
    UPDATE_ACCOUNT = "update_account"       # e.g. plan/seat changes
    ESCALATE_TO_HUMAN = "escalate_to_human"  # hand off entirely
    REQUEST_MORE_INFO = "request_more_info"  # ask the customer a clarifying question


class Decision(BaseModel):
    """The structured output of the Decision Engine for a single ticket."""

    intent: Intent
    urgency: Urgency
    recommended_action: RecommendedAction
    requires_human: bool
    reason: str


def decide_ticket(context: TicketContext) -> Decision:
    """Analyze a TicketContext and return a Decision.

    Not implemented yet — this milestone only defines the interface.
    The next milestone will fill this in with an LLM call (and later,
    risk-scoring rules that can override the LLM's own judgment).
    """
    raise NotImplementedError(
        "decide_ticket() is not implemented yet — the Decision Engine "
        "currently only defines the Decision model and function signature."
    )