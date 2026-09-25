import { useEffect, useState } from "react";
import "./App.css";

type Ticket = {
  id: number;
  subject: string;
  customer: string;
  initials: string;
  plan: string;
  email: string;
  priority: "HIGH" | "NORMAL" | "URGENT";
  message: string;

  // Demo/fallback values
  intent: string;
  urgency: string;
  action: string;
  autonomy: string;
  reason: string;
  riskScore: number;

  status?: string;
};

type ApiTicket = {
  id: number;
  subject: string;
  message: string;
  status: string;
  priority: string;
  created_at: string;
  customer: {
    id: number;
    name: string;
    email: string;
    plan: string;
    customer_value: number;
  };
};

type AIAnalysis = {
  decision: {
    ticket_id: number;
    intent: string;
    urgency: string;
    recommended_action: string;
    requires_human: boolean;
    reason: string;
  };
  risk: {
    level: string;
    risk_score: number;
    reasons: string[];
  };
};

const API_BASE_URL = "/api";

const fallbackTickets: Ticket[] = [
  {
    id: 1,
    subject: "Unable to export quarterly report",
    customer: "Priya Sharma",
    initials: "PS",
    plan: "Enterprise",
    email: "priya.sharma@nimbuscorp.com",
    priority: "HIGH",
    message:
      "Our finance team can't export the Q3 report, the export button just spins forever.",
    intent: "Technical issue",
    urgency: "High",
    action: "Escalate to human",
    autonomy: "Human approval",
    reason:
      "Enterprise customer with high lifetime value reporting a blocking technical issue affecting quarterly finance reporting. Human handling is required.",
    riskScore: 100,
  },
  {
    id: 2,
    subject: "Question about invoice",
    customer: "Rahul Mehta",
    initials: "RM",
    plan: "Pro",
    email: "rahul.mehta@example.com",
    priority: "NORMAL",
    message:
      "Could you explain the additional charge on my latest invoice?",
    intent: "Billing question",
    urgency: "Normal",
    action: "Reply to customer",
    autonomy: "Auto",
    reason:
      "This is a straightforward billing question that can be answered without changing customer or financial state.",
    riskScore: 0,
  },
  {
    id: 3,
    subject: "Change account email",
    customer: "Neha Kapoor",
    initials: "NK",
    plan: "Business",
    email: "neha.kapoor@example.com",
    priority: "NORMAL",
    message:
      "I need to update the email associated with my account.",
    intent: "Account change",
    urgency: "Normal",
    action: "Update account",
    autonomy: "Human approval",
    reason:
      "Changing account information affects customer identity data, so human approval is required before the action is executed.",
    riskScore: 25,
  },
  {
    id: 4,
    subject: "Refund request",
    customer: "Arjun Patel",
    initials: "AP",
    plan: "Enterprise",
    email: "arjun.patel@example.com",
    priority: "URGENT",
    message:
      "We were charged twice for the same subscription.",
    intent: "Refund request",
    urgency: "Urgent",
    action: "Issue refund",
    autonomy: "Human approval",
    reason:
      "This is a financial action involving an enterprise customer and an urgent duplicate-charge complaint. Human approval is required.",
    riskScore: 100,
  },
];

function App() {
  const [tickets, setTickets] = useState<Ticket[]>(fallbackTickets);
  const [selectedTicketId, setSelectedTicketId] = useState(1);

  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<AIAnalysis | null>(null);

  const [isExecuting, setIsExecuting] = useState(false);
  const [actionMessage, setActionMessage] = useState("");

  const selectedTicket =
    tickets.find((ticket) => ticket.id === selectedTicketId) ??
    tickets[0];

  useEffect(() => {
    loadTickets();
  }, []);

  async function loadTickets() {
    setIsLoading(true);
    setLoadError("");

    try {
      const response = await fetch(`${API_BASE_URL}/tickets`);

      if (!response.ok) {
        throw new Error("Could not load tickets from the backend.");
      }

      const data: ApiTicket[] = await response.json();

      const mappedTickets: Ticket[] = data.map((ticket) => {
        const fallback =
          fallbackTickets.find((item) => item.id === ticket.id) ??
          fallbackTickets[0];

        return {
          id: ticket.id,
          subject: ticket.subject,
          customer: ticket.customer.name,
          initials: ticket.customer.name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .slice(0, 2)
            .toUpperCase(),
          plan: ticket.customer.plan,
          email: ticket.customer.email,
          priority:
            ticket.priority.toUpperCase() as Ticket["priority"],
          message: ticket.message,

          intent: fallback.intent,
          urgency: fallback.urgency,
          action: fallback.action,
          autonomy: fallback.autonomy,
          reason: fallback.reason,
          riskScore: fallback.riskScore,

          status: ticket.status,
        };
      });

      if (mappedTickets.length > 0) {
        setTickets(mappedTickets);
        setSelectedTicketId(mappedTickets[0].id);
      }
    } catch (error) {
      setLoadError(
        error instanceof Error
          ? error.message
          : "Could not connect to the backend.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAnalyze() {
    if (!selectedTicket) {
      return;
    }

    setIsAnalyzing(true);
    setAiAnalysis(null);
    setActionMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tickets/${selectedTicket.id}/analyze`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "AI analysis failed.");
      }

      setAiAnalysis(data);
    } catch (error) {
      setActionMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong during AI analysis.",
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleEscalate() {
    if (!selectedTicket) {
      return;
    }

    setIsExecuting(true);
    setActionMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/tickets/${selectedTicket.id}/escalate`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? "The action failed.");
      }

      setActionMessage(data.message);

      setTickets((currentTickets) =>
        currentTickets.map((ticket) =>
          ticket.id === selectedTicket.id
            ? {
                ...ticket,
                status: "escalated",
              }
            : ticket,
        ),
      );
    } catch (error) {
      setActionMessage(
        error instanceof Error
          ? error.message
          : "Something went wrong while executing the action.",
      );
    } finally {
      setIsExecuting(false);
    }
  }

  function getDisplayIntent() {
    return aiAnalysis?.decision.intent ?? selectedTicket.intent;
  }

  function getDisplayUrgency() {
    return aiAnalysis?.decision.urgency ?? selectedTicket.urgency;
  }

  function getDisplayAction() {
    if (aiAnalysis) {
      return aiAnalysis.decision.recommended_action
        .replaceAll("_", " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }

    return selectedTicket.action;
  }

  function getDisplayAutonomy() {
    if (aiAnalysis) {
      return aiAnalysis.risk.level === "human_approval"
        ? "Human approval"
        : "Auto";
    }

    return selectedTicket.autonomy;
  }

  function getDisplayReason() {
    return aiAnalysis?.decision.reason ?? selectedTicket.reason;
  }

  function getDisplayRiskScore() {
    return aiAnalysis?.risk.risk_score ?? selectedTicket.riskScore;
  }

  function requiresHumanApproval() {
    if (aiAnalysis) {
      return (
        aiAnalysis.decision.requires_human ||
        aiAnalysis.risk.level === "human_approval"
      );
    }

    return selectedTicket.autonomy === "Human approval";
  }

  function getRiskReasons() {
    if (aiAnalysis?.risk.reasons?.length) {
      return aiAnalysis.risk.reasons;
    }

    if (selectedTicket.riskScore >= 50) {
      return [
        "AI decision requires human approval",
        `${selectedTicket.urgency} urgency ticket`,
        `AI recommends ${selectedTicket.action.toLowerCase()}`,
      ];
    }

    return [
      "No high-risk financial or account action detected",
      "Decision is eligible for autonomous execution",
    ];
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>CORA</h1>
            <span>Customer Operations</span>
          </div>
        </div>

        <nav>
          <button className="nav-item active">
            <span>▣</span>
            Inbox
            <span className="badge">{tickets.length}</span>
          </button>

          <button className="nav-item">
            <span>⚠</span>
            Approvals
            <span className="badge warning">
              {tickets.filter((ticket) => ticket.autonomy === "Human approval").length}
            </span>
          </button>

          <button className="nav-item">
            <span>◈</span>
            Metrics
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="agent-status">
            <span className="status-dot" />

            <div>
              <strong>AI Teammate Online</strong>
              <small>Autonomy system active</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">CUSTOMER SERVICE</p>
            <h2>AI Operations Center</h2>
          </div>

          <div className="topbar-right">
            <div className="system-pill">
              <span className="status-dot" />
              System operational
            </div>

            <div className="avatar">A</div>
          </div>
        </header>

        {loadError && (
          <div className="action-message">
            {loadError}
          </div>
        )}

        <section className="stats">
          <div className="stat-card">
            <span>Open tickets</span>
            <strong>{tickets.length}</strong>
            <small>
              {tickets.filter((ticket) => ticket.priority === "HIGH").length} high
              priority
            </small>
          </div>

          <div className="stat-card">
            <span>AI automation</span>
            <strong>68%</strong>
            <small>of eligible tickets</small>
          </div>

          <div className="stat-card">
            <span>Needs approval</span>
            <strong>
              {
                tickets.filter(
                  (ticket) => ticket.autonomy === "Human approval",
                ).length
              }
            </strong>
            <small>awaiting human review</small>
          </div>

          <div className="stat-card">
            <span>Actions completed</span>
            <strong>47</strong>
            <small>this week</small>
          </div>
        </section>

        <section className="workspace">
          <div className="ticket-list panel">
            <div className="panel-header">
              <div>
                <h3>Ticket Inbox</h3>
                <span>AI-prioritized customer issues</span>
              </div>

              <button className="filter-button">
                All tickets ▾
              </button>
            </div>

            <div className="tickets">
              {isLoading ? (
                <div style={{ padding: "20px", color: "#918b81" }}>
                  Loading tickets...
                </div>
              ) : (
                tickets.map((ticket) => (
                  <button
                    key={ticket.id}
                    className={`ticket ${
                      selectedTicketId === ticket.id ? "selected" : ""
                    }`}
                    onClick={() => {
                      setSelectedTicketId(ticket.id);
                      setActionMessage("");
                      setAiAnalysis(null);
                    }}
                  >
                    <div className="ticket-top">
                      <strong>{ticket.subject}</strong>

                      <span
                        className={`priority ${ticket.priority.toLowerCase()}`}
                      >
                        {ticket.priority}
                      </span>
                    </div>

                    <p>
                      {ticket.customer} · {ticket.plan}
                    </p>

                    <small>{ticket.message}</small>
                  </button>
                ))
              )}
            </div>
          </div>

          <div className="ticket-detail panel">
            <div className="detail-header">
              <div>
                <span className="ticket-id">
                  TICKET #{selectedTicket.id}
                </span>

                <h3>{selectedTicket.subject}</h3>
              </div>

              <span
                className={`priority ${selectedTicket.priority.toLowerCase()}`}
              >
                {selectedTicket.priority}
              </span>
            </div>

            <div className="customer">
              <div className="customer-avatar">
                {selectedTicket.initials}
              </div>

              <div>
                <strong>{selectedTicket.customer}</strong>
                <span>{selectedTicket.email}</span>
              </div>

              <div className="customer-plan">
                <span>{selectedTicket.plan.toUpperCase()}</span>

                <strong>
                  {selectedTicket.plan === "Enterprise"
                    ? "$48,000 LTV"
                    : selectedTicket.plan === "Business"
                      ? "$22,000 LTV"
                      : "$8,500 LTV"}
                </strong>
              </div>
            </div>

            <div className="message">
              <span className="section-label">
                CUSTOMER MESSAGE
              </span>

              <p>{selectedTicket.message}</p>
            </div>

            <div className="ai-section">
              <div className="section-heading">
                <span className="ai-icon">✦</span>

                <div>
                  <strong>AI Decision</strong>
                  <span>
                    {aiAnalysis
                      ? "Gemini Decision Engine · Live analysis"
                      : "Gemini Decision Engine · Awaiting analysis"}
                  </span>
                </div>
              </div>

              <div className="decision-grid">
                <div>
                  <span>Intent</span>
                  <strong>{getDisplayIntent()}</strong>
                </div>

                <div>
                  <span>Urgency</span>

                  <strong
                    className={
                      getDisplayUrgency() === "urgent" ||
                      getDisplayUrgency() === "high" ||
                      getDisplayUrgency() === "Urgent" ||
                      getDisplayUrgency() === "High"
                        ? "text-high"
                        : ""
                    }
                  >
                    {getDisplayUrgency()}
                  </strong>
                </div>

                <div>
                  <span>Recommended action</span>
                  <strong>{getDisplayAction()}</strong>
                </div>

                <div>
                  <span>Autonomy</span>

                  <strong
                    className={
                      getDisplayAutonomy() === "Human approval"
                        ? "text-warning"
                        : ""
                    }
                  >
                    {getDisplayAutonomy()}
                  </strong>
                </div>
              </div>

              <div className="reason">
                <span>AI reasoning</span>

                <p>{getDisplayReason()}</p>
              </div>
            </div>

            <div className="risk-section">
              <div className="risk-header">
                <div>
                  <span className="section-label">
                    RISK / AUTONOMY GATE
                  </span>

                  <strong>
                    {requiresHumanApproval()
                      ? "Human approval required"
                      : "Safe for autonomous execution"}
                  </strong>
                </div>

                <div className="risk-score">
                  <strong>{getDisplayRiskScore()}</strong>
                  <span>RISK SCORE</span>
                </div>
              </div>

              <div className="risk-bar">
                <div
                  style={{
                    width: `${getDisplayRiskScore()}%`,
                  }}
                />
              </div>

              <ul>
                {getRiskReasons().map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>

            {actionMessage && (
              <div className="action-message">
                {actionMessage}
              </div>
            )}

            <div className="action-row">
              <button
                className="secondary-button"
                onClick={handleAnalyze}
                disabled={isAnalyzing}
              >
                {isAnalyzing ? "Analyzing..." : "Analyze with AI"}
              </button>

              {requiresHumanApproval() ? (
                <>
                  <button
                    className="secondary-button"
                    onClick={() => {
                      setActionMessage(
                        "Action rejected by operator. No backend action was executed.",
                      );
                    }}
                    disabled={isExecuting}
                  >
                    Reject
                  </button>

                  <button
                    className="primary-button"
                    onClick={handleEscalate}
                    disabled={isExecuting}
                  >
                    {isExecuting
                      ? "Executing..."
                      : "Approve & Execute"}
                  </button>
                </>
              ) : (
                <button
                  className="primary-button"
                  onClick={() =>
                    setActionMessage(
                      "This action is eligible for autonomous execution, but an executor tool is not implemented for this action yet.",
                    )
                  }
                >
                  Execute Action
                </button>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;