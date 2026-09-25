"""
Decision Engine.

Given a TicketContext, this module asks Gemini to analyze the ticket
and return a structured Decision describing what should happen next.

The model only REASONS here. It does not take actions and does not
call tools. Risk scoring is handled separately by the deterministic
Risk / Autonomy Gate.
"""

import os
import json
from enum import Enum

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from app.agent.context_builder import TicketContext


load_dotenv()

GEMINI_MODEL = "gemini-3.8-flash"


class DecisionEngineError(Exception):
    """Raised when the Decision Engine can't produce a Decision."""


class Intent(str, Enum):
    BILLING_QUESTION = "billing_question"
    REFUND_REQUEST = "refund_request"
    TECHNICAL_ISSUE = "technical_issue"
    ACCOUNT_CHANGE = "account_change"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    GENERAL_INQUIRY = "general_inquiry"
    OTHER = "other"


class Urgency(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class RecommendedAction(str, Enum):
    AUTO_RESOLVE = "auto_resolve"
    REPLY_TO_CUSTOMER = "reply_to_customer"
    ISSUE_REFUND = "issue_refund"
    UPDATE_ACCOUNT = "update_account"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    REQUEST_MORE_INFO = "request_more_info"


class Decision(BaseModel):
    ticket_id: int
    intent: Intent
    urgency: Urgency
    recommended_action: RecommendedAction
    requires_human: bool
    reason: str


def _get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise DecisionEngineError(
            "GEMINI_API_KEY is not set. Add it to your project-root .env file."
        )

    return genai.Client(api_key=api_key)


def _build_prompt(context: TicketContext) -> str:
    return f"""
You are CORA, an AI customer-service teammate working alongside a human
support team.

Your job is to ANALYZE the support ticket and decide what should happen next.

You DO NOT execute actions.
You DO NOT call tools.
You ONLY reason about the ticket and return the structured decision.

CUSTOMER
Name: {context.customer_name}
Email: {context.customer_email}
Plan: {context.customer_plan}
Lifetime value: ${context.customer_value:,.2f}

TICKET
Ticket ID: {context.ticket_id}
Subject: {context.ticket_subject}
Message: {context.ticket_message}
Current status: {context.ticket_status}
Current priority: {context.ticket_priority}
Created at: {context.ticket_created_at.isoformat()}

DECISION GUIDELINES

1. Identify the customer's intent.

2. Determine urgency:
   - low
   - normal
   - high
   - urgent

3. Recommend exactly one action:
   - auto_resolve
   - reply_to_customer
   - issue_refund
   - update_account
   - escalate_to_human
   - request_more_info

4. Set requires_human to true when:
   - the action changes financial state
   - the action changes account/customer information
   - the issue is urgent or highly sensitive
   - the customer is enterprise or high-value and the situation warrants caution
   - the customer appears angry or the issue could have legal consequences
   - human escalation is explicitly recommended

5. Simple informational questions can generally be answered without human
   approval.

The ticket_id MUST be exactly {context.ticket_id}.

Return ONLY the structured JSON object requested by the response schema.
Do not include markdown.
Do not include ```json.
Do not include explanations outside the JSON object.
""".strip()


def _get_response_schema() -> dict:
    """
    Explicit JSON schema for Gemini.

    We intentionally define this schema manually instead of passing
    Pydantic's generated schema directly. This avoids enum/$defs/reference
    complexity while still validating the final result with Pydantic.
    """

    return {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "integer",
            },
            "intent": {
                "type": "string",
                "enum": [
                    "billing_question",
                    "refund_request",
                    "technical_issue",
                    "account_change",
                    "feature_request",
                    "complaint",
                    "general_inquiry",
                    "other",
                ],
            },
            "urgency": {
                "type": "string",
                "enum": [
                    "low",
                    "normal",
                    "high",
                    "urgent",
                ],
            },
            "recommended_action": {
                "type": "string",
                "enum": [
                    "auto_resolve",
                    "reply_to_customer",
                    "issue_refund",
                    "update_account",
                    "escalate_to_human",
                    "request_more_info",
                ],
            },
            "requires_human": {
                "type": "boolean",
            },
            "reason": {
                "type": "string",
            },
        },
        "required": [
            "ticket_id",
            "intent",
            "urgency",
            "recommended_action",
            "requires_human",
            "reason",
        ],
    }


def decide_ticket(context: TicketContext) -> Decision:
    client = _get_client()
    prompt = _build_prompt(context)

    try:
        interaction = client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": _get_response_schema(),
            },
        )
    except Exception as exc:
        raise DecisionEngineError(
            f"Gemini API call failed: {exc}"
        ) from exc

    raw_output = getattr(interaction, "output_text", None)

    if not raw_output:
        raise DecisionEngineError(
            "Gemini returned an empty response."
        )

    raw_output = raw_output.strip()

    try:
        parsed_output = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise DecisionEngineError(
            "Gemini returned invalid JSON.\n"
            f"Raw response was: {raw_output}"
        ) from exc

    try:
        return Decision.model_validate(parsed_output)
    except Exception as exc:
        raise DecisionEngineError(
            "Gemini returned JSON, but it did not match the Decision model.\n"
            f"Validation error: {exc}\n"
            f"Parsed response: {parsed_output}"
        ) from exc