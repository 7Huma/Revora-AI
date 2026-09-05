import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function AgentDecision({
  caseData,
  onClose,
}) {
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] =
    useState(true);

  const [executing, setExecuting] =
    useState(false);

  const [executionResult, setExecutionResult] =
    useState(null);

  const [executionError, setExecutionError] =
    useState("");

  useEffect(() => {
    if (!caseData?.id) return;

    loadHistory(caseData.id);
  }, [caseData]);

  const loadHistory = async (id) => {
    try {
      setLoadingHistory(true);

      const data =
        await api.interventionHistory(id);

      setHistory(data);
    } catch (e) {
      console.error(e);
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  };

  if (!caseData) return null;

  // ============================================================
  // CASE DATA
  // ============================================================

  const risk = Number(
    caseData.risk_score || 0
  );

  const riskLabel =
    risk >= 70
      ? "HIGH"
      : risk >= 40
      ? "MEDIUM"
      : "LOW";

  const recoveryProbability = Math.round(
    Number(
      caseData.recovery_probability || 0
    ) * 100
  );

  const expectedRecovery = Number(
    caseData.expected_recovery || 0
  );

  const amountAtRisk = Number(
    caseData.amount_at_risk || 0
  );

  const status = String(
    caseData.status || ""
  ).toUpperCase();

  const rootCause = String(
    caseData.root_cause || "UNKNOWN"
  ).replaceAll("_", " ");

  const suggestedAction = String(
    caseData.suggested_action ||
      "MANUAL REVIEW"
  ).replaceAll("_", " ");

  const source = String(
  caseData.source || ""
).toLowerCase();

const interventionPlan = {
  payment_failure: {
    channel: "PAYMENT RETRY",
    reason:
      "The payment failure may be recoverable automatically, so retrying the payment is preferred before escalating to customer support.",
  },

  checkout_abandonment: {
    channel: "EMAIL",
    reason:
      "The customer demonstrated purchase intent by starting checkout. A targeted recovery message can bring them back without unnecessary manual intervention.",
  },

  subscription_failure: {
    channel: "PAYMENT RETRY",
    reason:
      "The recurring payment failed while the subscription is still recoverable. An automated retry is the lowest-friction recovery path.",
  },

  overdue_invoice: {
    channel: "EMAIL",
    reason:
      "This is an outstanding B2B receivable. A targeted payment reminder is more appropriate than an automatic payment retry.",
  },

  mandate_retry: {
    channel: "PAYMENT RETRY",
    reason:
      "The recurring mandate failed but can potentially be recovered through another payment attempt before manual escalation.",
  },
};

const selectedIntervention =
  interventionPlan[source] || {
    channel: "MANUAL REVIEW",
    reason:
      "The case does not match a predefined automated recovery path, so manual review is recommended.",
  };

  const intelligence =
    caseData.ai_intelligence || {};

  const whyNow =
    intelligence.why_now ||
    caseData.agent_reason ||
    caseData.reason ||
    "The AI detected a revenue recovery opportunity.";

  const whyAction =
    intelligence.why_action ||
    caseData.agent_reason ||
    "The selected intervention was determined from the detected revenue risk.";

  const signals =
    Array.isArray(intelligence.signals) &&
    intelligence.signals.length
      ? intelligence.signals
      : [
          `₹${amountAtRisk.toLocaleString()} revenue exposure`,
          `Risk score: ${risk}/100`,
          `Root cause: ${rootCause}`,
        ];

  const priority =
    intelligence.priority ||
    riskLabel;

  // ============================================================
  // EXECUTE AI RECOVERY
  // ============================================================

  const executeRecovery = async () => {
  try {
    setExecutionError("");
    setExecutionResult(null);
    setExecuting(true);

    const channel =
      selectedIntervention.channel
        .toLowerCase()
        .replaceAll(" ", "_");

    const result = await api.execute(
      caseData.id,
      channel
    );

    setExecutionResult(result);

    await loadHistory(caseData.id);

  } catch (e) {
    console.error(e);

    setExecutionError(
      "Recovery execution failed. Please try again."
    );
  } finally {
    setExecuting(false);
  }
};
  const canExecute =
    status === "OPEN" &&
    !executing;

  return (
    <>
      {/* ========================================================
          OVERLAY
      ======================================================== */}

      <div
        className="drawer-overlay"
        onClick={onClose}
      />

      {/* ========================================================
          DRAWER
      ======================================================== */}

      <aside className="agent-drawer">

        {/* HEADER */}

        <div className="drawer-header">
          <div>
            <p className="eyebrow">
              AI AGENT
            </p>

            <h2>
              AI Recovery Decision
            </h2>

            <p className="ai-subtitle">
              Explainable revenue recovery analysis
            </p>
          </div>

          <button
            className="drawer-close"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        {/* ======================================================
            SCORE CARDS
        ====================================================== */}

        <div className="ai-score-grid">

          <div className="ai-score-card">
            <span>
              RISK SCORE
            </span>

            <strong>
              {risk}/100
            </strong>

            <small>
              {riskLabel}
            </small>
          </div>

          <div className="ai-score-card">
            <span>
              RECOVERY PROBABILITY
            </span>

            <strong>
              {recoveryProbability}%
            </strong>

            <small>
              AI estimate
            </small>
          </div>

          <div className="ai-score-card expected">
            <span>
              EXPECTED RECOVERY
            </span>

            <strong>
              ₹
              {expectedRecovery.toLocaleString()}
            </strong>

            <small>
              confidence-weighted opportunity
            </small>
          </div>

        </div>

        {/* ======================================================
            AI PRIORITY
        ====================================================== */}

        <section className="ai-priority-card">

          <div className="ai-priority-header">
            <div>
              <p className="eyebrow">
                AI PRIORITY
              </p>

              <h3>
                {priority}
              </h3>
            </div>

            <span
              className={`ai-priority-badge ${priority.toLowerCase()}`}
            >
              {priority}
            </span>
          </div>

          <p>
            {priority === "HIGH"
              ? "Immediate recovery attention recommended."
              : priority === "MEDIUM"
              ? "Recovery opportunity should be addressed soon."
              : "Lower urgency recovery opportunity."}
          </p>

        </section>

        {/* ======================================================
            DECISION TRACE
        ====================================================== */}

        <section className="decision-trace">

          <div className="trace-header">
            <div>
              <p className="eyebrow">
                AI DECISION TRACE
              </p>

              <h3>
                How the recovery decision was made
              </h3>
            </div>
          </div>

          <div className="trace-step">
            <div className="trace-number">
              1
            </div>

            <div>
              <strong>
                Revenue risk detected
              </strong>

              <p>
                ₹
                {amountAtRisk.toLocaleString()}{" "}
                identified as at-risk revenue.
              </p>
            </div>
          </div>

          <div className="trace-step">
            <div className="trace-number">
              2
            </div>

            <div>
              <strong>
                Risk scored
              </strong>

              <p>
                Risk score: {risk}/100 ·{" "}
                {riskLabel} priority
              </p>
            </div>
          </div>

          <div className="trace-step">
            <div className="trace-number">
              3
            </div>

            <div>
              <strong>
                Root cause diagnosed
              </strong>

              <p>
                {rootCause}
              </p>
            </div>
          </div>

          <div className="trace-step">
            <div className="trace-number">
              4
            </div>

            <div>
              <strong>
                Recovery probability estimated
              </strong>

              <p>
                AI estimates a{" "}
                {recoveryProbability}%{" "}
                probability of successful recovery.
              </p>
            </div>
          </div>

          <div className="trace-step">
            <div className="trace-number">
              5
            </div>

            <div>
              <strong>
                Intervention selected
              </strong>

              <p>
                {suggestedAction}
              </p>
            </div>
          </div>

        </section>

        {/* ======================================================
            WHY NOW
        ====================================================== */}

        <section className="ai-insight-card">

          <div className="ai-insight-header">
            <span className="ai-insight-icon">
              ⚡
            </span>

            <div>
              <p className="eyebrow">
                WHY NOW?
              </p>

              <h3>
                Why this case matters
              </h3>
            </div>
          </div>

          <p>
            {whyNow}
          </p>

        </section>

        {/* ======================================================
            KEY SIGNALS
        ====================================================== */}

        <section className="ai-signals">

          <div className="ai-section-heading">
            <p className="eyebrow">
              KEY SIGNALS
            </p>

            <h3>
              Evidence used by the agent
            </h3>
          </div>

          <div className="signal-list">

            {signals.map(
              (signal, index) => (
                <div
                  className="signal-item"
                  key={index}
                >
                  <span className="signal-check">
                    ✓
                  </span>

                  <span>
                    {signal}
                  </span>
                </div>
              )
            )}

          </div>

        </section>

        {/* ======================================================
            ROOT CAUSE
        ====================================================== */}

        <div className="decision-row">

          <span>
            ROOT CAUSE
          </span>

          <strong>
            {rootCause}
          </strong>

        </div>

        {/* ======================================================
            WHY ACTION
        ====================================================== */}

        <section className="ai-insight-card action-reason">

          <div className="ai-insight-header">
            <span className="ai-insight-icon">
              ◎
            </span>

            <div>
              <p className="eyebrow">
                WHY THIS ACTION?
              </p>

              <h3>
                Intervention logic
              </h3>
            </div>
          </div>

          <p>
            {whyAction}
          </p>

        </section>
        
        {/* ======================================================
    SMART INTERVENTION SELECTION
====================================================== */}

<section className="smart-intervention">

  <div className="smart-intervention-header">

    <div>
      <p className="eyebrow">
        SMART INTERVENTION
      </p>

      <h3>
        Best recovery channel
      </h3>
    </div>

    <span className="channel-badge">
      AI SELECTED
    </span>

  </div>

  <div className="selected-channel">

    <div className="channel-icon">
      {selectedIntervention.channel === "EMAIL"
        ? "✉"
        : selectedIntervention.channel ===
          "PAYMENT RETRY"
        ? "↻"
        : "●"}
    </div>

    <div>
      <span>
        SELECTED CHANNEL
      </span>

      <strong>
        {selectedIntervention.channel}
      </strong>
    </div>

  </div>

  <div className="channel-reason">

    <span>
      WHY THIS CHANNEL?
    </span>

    <p>
      {selectedIntervention.reason}
    </p>

  </div>

</section>

        {/* ======================================================
            RECOMMENDED ACTION
        ====================================================== */}

        <div className="recommended-action">

          <span>
            RECOMMENDED ACTION
          </span>

          <strong>
            {suggestedAction}
          </strong>

        </div>

        {/* ======================================================
            EXECUTION ERROR
        ====================================================== */}

        {executionError && (
          <div className="execution-error">
            {executionError}
          </div>
        )}

        {/* ======================================================
            EXECUTE AI RECOVERY
        ====================================================== */}

        {status === "OPEN" && (
          <section className="ai-execute-panel">

            <div>
              <p className="eyebrow">
                AUTONOMOUS RECOVERY
              </p>

              <h3>
                Ready to execute
              </h3>

              <p>
                The AI has selected{" "}
                <strong>
                  {suggestedAction}
                </strong>{" "}
                as the next recovery intervention.
              </p>
            </div>

            <button
              className="ai-execute-button"
              onClick={executeRecovery}
              disabled={!canExecute}
            >
              {executing
                ? "Executing AI Recovery..."
                : "Execute AI Recovery"}
            </button>

          </section>
        )}

        {/* ======================================================
            EXECUTION RESULT
        ====================================================== */}

        {executionResult && (
          <section className="execution-result">

            <div className="execution-result-icon">
              ✓
            </div>

            <div>
              <p className="eyebrow">
                AGENT OUTCOME
              </p>

              <h3>
                Recovery action executed
              </h3>

              <p>
                The intervention was successfully
                recorded in the recovery history.
              </p>

              <strong>
                ₹
                {Number(
                  executionResult.recovered_amount ||
                    0
                ).toLocaleString()}
                {" "}recovered
              </strong>
            </div>

          </section>
        )}

        {/* ======================================================
            AI REASONING
        ====================================================== */}

        <section className="ai-reasoning">

          <h3>
            AI reasoning
          </h3>

          <p>
            {caseData.agent_reason ||
              caseData.reason_detail ||
              "The recovery agent selected an intervention based on the detected revenue risk."}
          </p>

        </section>

        {/* ======================================================
            STATS
        ====================================================== */}

        <div className="drawer-stats">

          <div>
            <span>
              AT RISK
            </span>

            <strong>
              ₹
              {amountAtRisk.toLocaleString()}
            </strong>
          </div>

          <div>
            <span>
              STATUS
            </span>

            <strong>
              {executionResult
                ? String(
                    executionResult.case_status ||
                      "RECOVERED"
                  ).toUpperCase()
                : status}
            </strong>
          </div>

        </div>

        {/* ======================================================
            INTERVENTION HISTORY
        ====================================================== */}

        <section className="intervention-history">

          <div className="history-header">

            <h3>
              Intervention History
            </h3>

            <span>
              {history.length}
            </span>

          </div>

          {loadingHistory ? (

            <p className="history-empty">
              Loading history...
            </p>

          ) : history.length === 0 ? (

            <p className="history-empty">
              No interventions yet.
            </p>

          ) : (

            <div className="timeline">

              {history.map(
                (item) => (
                  <div
                    className="timeline-item"
                    key={item.id}
                  >

                    <div className="timeline-dot" />

                    <div>

                      <strong>
                        {String(
                          item.type || ""
                        ).replaceAll(
                          "_",
                          " "
                        )}
                      </strong>

                      <p>
                        {item.channel}
                      </p>

                      <small>
                        {item.result}
                        {" · "}
                        {new Date(
                          item.executed_at
                        ).toLocaleString()}
                      </small>

                    </div>

                  </div>
                )
              )}

            </div>

          )}

        </section>

      </aside>
    </>
  );
}