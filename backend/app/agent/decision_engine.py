"""
Decision Engine.

Given a TicketContext, this module asks Gemini to analyze the ticket
and return a structured Decision describing what should happen next.

The model only REASONS here — it does not take actions and does not
call tools. Risk scoring (a deterministic policy layer that can
override the LLM's judgment) is a later milestone.
"""

import os
from enum import Enum

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from app.agent.context_builder import TicketContext

# Loads GEMINI_API_KEY (and anything else) from the project-root .env file.
# Safe to call even if no .env file exists.
load_dotenv()

GEMINI_MODEL = "gemini-3.8-flash"


class DecisionEngineError(Exception):
    """Raised when the Decision Engine can't produce a Decision.

    Covers: a missing API key, a failed Gemini API call, or a response
    that can't be parsed into a Decision.
    """


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


def _get_client() -> genai.Client:
    """Build a Gemini client using the API key from the environment.

    Never hard-code the key — it must come from GEMINI_API_KEY, loaded
    from the project-root .env file (see load_dotenv() above).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise DecisionEngineError(
            "GEMINI_API_KEY is not set. Add it to your project-root .env "
            "file, e.g.:\nGEMINI_API_KEY=your-key-here"
        )
    return genai.Client(api_key=api_key)


def _build_prompt(context: TicketContext) -> str:
    """Turn a TicketContext into a clear instruction prompt for Gemini."""
    return f"""
You are an AI customer-service teammate working alongside a human support team.

Your job right now is to ANALYZE this support ticket and decide what should
happen next. You do NOT take any action and you do NOT call any tools —
you only reason about the ticket and return a structured decision.

Customer:
- Name: {context.customer_name}
- Email: {context.customer_email}
- Plan: {context.customer_plan}
- Lifetime value: ${context.customer_value:,.2f}

Ticket:
- Subject: {context.ticket_subject}
- Message: {context.ticket_message}
- Current status: {context.ticket_status}
- Current priority: {context.ticket_priority}
- Created at: {context.ticket_created_at.isoformat()}

Take the customer's plan and lifetime value into account. Be more cautious
(prefer escalate_to_human) for enterprise or high-value customers, for
refund/account-change requests, and for anything that sounds urgent, angry,
or legally sensitive. Simple informational questions from any customer can
usually be auto-resolved or answered directly.

Respond with a decision that includes: the customer's intent, the urgency,
the recommended next action, whether a human must approve it, and a short
reason explaining your thinking.
""".strip()


def decide_ticket(context: TicketContext) -> Decision:
    """Ask Gemini to analyze a TicketContext and return a structured Decision.

    Raises:
        DecisionEngineError: if the API key is missing, the Gemini call
            fails, or the response can't be parsed into a Decision.
    """
    client = _get_client()
    prompt = _build_prompt(context)

    try:
        interaction = client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": Decision.model_json_schema(),
            },
        )
    except Exception as exc:
        raise DecisionEngineError(f"Gemini API call failed: {exc}") from exc

    raw_output = getattr(interaction, "output_text", None)
    if not raw_output:
        raise DecisionEngineError("Gemini returned an empty response.")

    try:
        return Decision.model_validate_json(raw_output)
    except Exception as exc:
        raise DecisionEngineError(
            f"Could not parse Gemini's response into a Decision: {exc}\n"
            f"Raw response was: {raw_output}"
        ) from exc