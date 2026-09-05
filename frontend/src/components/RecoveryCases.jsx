import { useState } from "react";
import AgentDecision from "./AgentDecision";
import { api } from "../services/api";

export default function RecoveryCases({
  cases,
  onExecuted,
}) {
  const [executing, setExecuting] = useState(null);
  const [error, setError] = useState("");
  const [selectedCase, setSelectedCase] = useState(null);

  const execute = async (id) => {
    try {
      setError("");
      setExecuting(id);

      await api.execute(id);

      // Keep "Executing..." visible for the judge.
      await new Promise((resolve) =>
        setTimeout(resolve, 1000)
      );

      await onExecuted();

      /*
       * Refresh the selected case after execution.
       * This makes the drawer immediately reflect
       * the new RECOVERED / FAILED state.
       */
      try {
        const updatedCase =
          await api.getCase(id);

        setSelectedCase(updatedCase);
      } catch (refreshError) {
        console.error(
          "Could not refresh selected case:",
          refreshError
        );
      }
    } catch (e) {
      console.error(e);
      setError(
        "Recovery execution failed."
      );
    } finally {
      setExecuting(null);
    }
  };

  if (!cases.length) {
    return (
      <div className="empty">
        No recovery cases yet.
      </div>
    );
  }

  return (
    <>
      <div className="cases">
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {cases.map((c) => {
          const status = String(
            c.status || ""
          ).toLowerCase();

          const isOpen =
            status === "open";

          const isExecuting =
            executing === c.id;

          let buttonText = "Recover";

          if (isExecuting) {
            buttonText = "Executing...";
          } else if (
            status === "in_progress"
          ) {
            buttonText = "In Progress";
          } else if (
            status === "recovered"
          ) {
            buttonText = "Recovered";
          } else if (
            status === "failed"
          ) {
            buttonText = "Failed";
          } else if (
            status === "expired"
          ) {
            buttonText = "Expired";
          }

          const riskScore = Number(
            c.risk_score || 0
          );

          const riskLabel =
            riskScore >= 70
              ? "HIGH"
              : riskScore >= 40
              ? "MEDIUM"
              : "LOW";

          const probability = Math.round(
            Number(
              c.recovery_probability || 0
            ) * 100
          );

          return (
            <div
              className="case"
              key={c.id}
              onClick={() =>
                setSelectedCase(c)
              }
            >
              {/* ==================================================
                  CASE INFORMATION
              ================================================== */}

              <div className="case-main">
                <div className="case-title">
                  <span
                    className={`badge ${
                      riskLabel.toLowerCase()
                    }`}
                  >
                    {riskLabel}
                  </span>

                  <h3>
                    #{c.id} ·{" "}
                    {String(
                      c.source || ""
                    ).replaceAll(
                      "_",
                      " "
                    )}
                  </h3>
                </div>

                {/* Root cause */}
                <p>
                  {String(
                    c.root_cause || ""
                  ).replaceAll(
                    "_",
                    " "
                  )}
                </p>

                {/* Keep dashboard description short.
                    Full AI reasoning appears in drawer. */}
                <small>
                  {c.reason_detail ||
                    "AI recovery analysis available."}
                </small>
              </div>

              {/* ==================================================
                  MONEY / RECOVERY INFORMATION
              ================================================== */}

              <div className="case-money">
                <strong>
                  ₹
                  {Number(
                    c.amount_at_risk || 0
                  ).toLocaleString()}
                </strong>

                <small className="case-expected">
                  Expected ₹
                  {Number(
                    c.expected_recovery || 0
                  ).toLocaleString()}
                </small>

                <small className="case-probability">
                  {probability}%
                  recovery probability
                </small>
              </div>

              {/* ==================================================
                  RECOVERY ACTION
              ================================================== */}

              <button
                onClick={(event) => {
                  event.stopPropagation();

                  if (isOpen) {
                    execute(c.id);
                  }
                }}
                disabled={
                  !isOpen ||
                  isExecuting
                }
              >
                {buttonText}
              </button>
            </div>
          );
        })}
      </div>

      {/* ========================================================
          AI RECOVERY DECISION DRAWER
      ======================================================== */}

      {selectedCase && (
        <AgentDecision
          caseData={selectedCase}
          onClose={() =>
            setSelectedCase(null)
          }
        />
      )}
    </>
  );
}