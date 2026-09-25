<div align="center">

# ✦ CORA

### Contextual Operations & Resolution Agent

**From customer issue to resolved outcome.**

An AI customer-service teammate that understands context,  
makes decisions, evaluates risk, and executes support actions.

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-AI-8E75B2?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

<br>

**Customer Service / Customer Operations**

</div>

---

# 🧠 What is CORA?

**CORA** stands for:

> **Contextual Operations & Resolution Agent**

CORA is an AI customer-service teammate designed to move beyond
chat-based support.


CORA (Contextual Operations & Resolution Agent) is an AI-powered customer-service teammate designed to transform support operations from simple question-answering into controlled, actionable workflows. 
It receives a customer ticket, builds a complete context using customer and ticket information, and uses Gemini to understand the customer's intent, determine urgency, recommend an appropriate action, and explain its reasoning. 
The resulting AI decision is then passed through a deterministic Risk / Autonomy Gate, which evaluates whether the proposed action can be performed autonomously or requires human approval. 
Low-risk operations can follow an automated execution path, while sensitive actions involving financial changes, account information, urgent issues, or human escalation are routed to an operator for approval. 
Once approved, CORA executes the supported action through backend tools and updates the ticket state. 
In this way, CORA combines AI reasoning, deterministic safety controls, human oversight, and real operational execution to act as a teammate that helps move a customer issue from context → decision → approval → action → resolution.




```text



_________________________________________________________________________________________________________________________________










SYSTEM ARCHITECTURE

┌──────────────────────────────────────────────────────────────┐
│                        CORA DASHBOARD                        │
│                   React + TypeScript + Vite                  │
│                                                              │
│  Ticket Inbox   │   Customer Context   │   AI Decision       │
│                 │                     │                     │
│                 │                     │   Risk Gate         │
│                 │                     │   Approval           │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ REST API
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    Context Builder                     │  │
│  │                                                        │  │
│  │ Customer + Ticket + Priority + Plan + Value + Status  │  │
│  └───────────────────────────┬────────────────────────────┘  │
│                              │                               │
│                              ▼                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                 Gemini Decision Engine                 │  │
│  │                                                        │  │
│  │ Intent │ Urgency │ Recommended Action │ Reasoning     │  │
│  └───────────────────────────┬────────────────────────────┘  │
│                              │                               │
│                              ▼                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                 Risk / Autonomy Gate                  │  │
│  │                                                        │  │
│  │       AUTO                 HUMAN_APPROVAL              │  │
│  └───────────────────────────┬────────────────────────────┘  │
│                              │                               │
│                              ▼                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    Action Executor                    │  │
│  └───────────────────────────┬────────────────────────────┘  │
└──────────────────────────────┼───────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
        ┌───────────────┐             ┌───────────────┐
        │    SQLite     │             │    Gemini     │
        │               │             │      API      │
        │ Customers     │             │               │
        │ Tickets       │             │ AI Reasoning  │
        │ State         │             │ Structured    │
        └───────────────┘             │ Output        │
                                      └───────────────┘









┌───────────────────────────────────────────────┐
│                  CORA UI                      │
│             React + TypeScript                │
│                                               │
│  Ticket Inbox → AI Decision → Risk → Action   │
└──────────────────────┬────────────────────────┘
                       │
                       │ REST API
                       ▼
┌───────────────────────────────────────────────┐
│               FastAPI Backend                 │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │          Context Builder                │  │
│  └──────────────────┬──────────────────────┘  │
│                     ▼                         │
│  ┌─────────────────────────────────────────┐  │
│  │        Gemini Decision Engine           │  │
│  └──────────────────┬──────────────────────┘  │
│                     ▼                         │
│  ┌─────────────────────────────────────────┐  │
│  │       Risk / Autonomy Gate              │  │
│  └──────────────────┬──────────────────────┘  │
│                     ▼                         │
│  ┌─────────────────────────────────────────┐  │
│  │          Action Executor                │  │
│  └──────────────────┬──────────────────────┘  │
└─────────────────────┼─────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │    SQLite     │
              │ Tickets +     │
              │ Customers     │
              └───────────────┘

                      │
                      ▼
              ┌───────────────┐
              │ Gemini API    │
              │ Decision      │
              │ Reasoning     │
              └───────────────┘








_________________________________________________________________________________________________________________________________







| Capability                | Description                                            |
| ------------------------  | ------------------------------------------------------ |
| 🧠 AI Ticket Analysis     | Uses Gemini to understand incoming support tickets     |
| 👤 Customer Context       | Considers customer identity, plan and lifetime value   |
| 🎯 Intent Detection       | Determines what the customer is actually asking for    |
| ⚡ Urgency Detection      | Classifies ticket urgency                              |
| 🧭 Action Recommendation  | Determines the appropriate next action                 |
| ⚖️ Risk Evaluation        | Calculates whether autonomous execution is appropriate |
| 👨‍💼 Human Approval         | Routes sensitive actions to an operator                |
| ⚙️ Action Execution       | Executes supported operational actions                 |
| 🗃️ Persistent State       | Updates ticket state in SQLite                         |
| 🖥️ Operator Dashboard     | Provides a visual support operations interface         |








________________________________________________________________________________________________________________________________





Supported actions





auto_resolve
reply_to_customer
issue_refund
update_account
escalate_to_human
request_more_info






_________________________________________________________________________________________________________________________________





BACKEND ARCHITECTURE



backend/
│
└── app/
    │
    ├── main.py
    │   └── FastAPI API
    │
    ├── agent/
    │   ├── context_builder.py
    │   │   └── Builds ticket context
    │   │
    │   ├── decision_engine.py
    │   │   └── Gemini reasoning
    │   │
    │   ├── risk_scorer.py
    │   │   └── Deterministic safety gate
    │   │
    │   └── executor.py
    │       └── Execution control
    │
    ├── models/
    │   ├── customer.py
    │   ├── ticket.py
    │   └── approval.py
    │
    ├── db/
    │   ├── session.py
    │   └── seed_data.py
    │
    └── tools/
        └── ticket_tool.py








_________________________________________________________________________________________________________________________________





FRONTEND ARCHITECTURE



frontend/
│
├── src/
│   ├── App.tsx
│   │   └── Main CORA interface
│   │
│   ├── App.css
│   │   └── Dashboard styling
│   │
│   └── ...
│
├── package.json
└── vite.config.ts





_________________________________________________________________________________________________________________________________



📁 Project Structure

AI-teammate/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── db/
│   │   ├── models/
│   │   ├── tools/
│   │   ├── config.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── .env                 # Local only
├── .gitignore
├── README.md
└── aiteammate.db        # Local database