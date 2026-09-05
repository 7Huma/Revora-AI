import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Analytics() {
  const [summary, setSummary] = useState(null);
  const [cases, setCases] = useState([]);

  useEffect(() => {
    Promise.all([
      api.summary(),
      api.cases(),
    ]).then(([s, c]) => {
      setSummary(s);
      setCases(c);
    });
  }, []);

  const atRisk = summary?.revenue_at_risk ?? 0;
  const recovered = summary?.recovered_revenue ?? 0;

  const recoveryRate =
    atRisk > 0
      ? Math.round((recovered / atRisk) * 100)
      : 0;

  // Group revenue by root cause
  const rootCauseTotals = cases.reduce((acc, c) => {
    const rootCause = String(
      c.root_cause || "UNKNOWN"
    ).replaceAll("_", " ");

    const amount = Number(c.amount_at_risk || 0);

    acc[rootCause] = (acc[rootCause] || 0) + amount;

    return acc;
  }, {});

  return (
    <>
      <header>
        <div>
          <p className="eyebrow">
            Revora AI
          </p>

          <h1>Analytics</h1>

          <p className="subtitle">
            Understand how effectively Revora AIS
            is recovering lost revenue.
          </p>
        </div>
      </header>

      {/* TOP METRICS */}
      <section className="analytics-grid">
        <div className="analytics-card">
          <span>REVENUE AT RISK</span>
          <strong>
            ₹{atRisk.toLocaleString()}
          </strong>
        </div>

        <div className="analytics-card">
          <span>RECOVERED</span>
          <strong>
            ₹{recovered.toLocaleString()}
          </strong>
        </div>

        <div className="analytics-card">
          <span>RECOVERY RATE</span>
          <strong>
            {recoveryRate}%
          </strong>
        </div>
      </section>

      {/* PERFORMANCE */}
      <section className="panel">
        <div className="panel-header">
          <h2>Revenue Recovery Performance</h2>
        </div>

        <div className="revenue-bars">
          <div className="bar-group">
            <div
              className="bar at-risk"
              style={{
                height: `${Math.max(
                  30,
                  Math.min(100, atRisk / 400)
                )}%`,
              }}
            />

            <span>At Risk</span>

            <strong>
              ₹{atRisk.toLocaleString()}
            </strong>
          </div>

          <div className="bar-group">
            <div
              className="bar recovered"
              style={{
                height: `${Math.max(
                  15,
                  Math.min(100, recovered / 400)
                )}%`,
              }}
            />

            <span>Recovered</span>

            <strong>
              ₹{recovered.toLocaleString()}
            </strong>
          </div>
        </div>
      </section>

      {/* ROOT CAUSE */}
      <section className="panel">
        <div className="panel-header">
          <h2>Recovery by Root Cause</h2>
        </div>

        {Object.entries(rootCauseTotals).map(
          ([rootCause, amount]) => (
            <div
              className="analytics-row"
              key={rootCause}
            >
              <span>{rootCause}</span>

              <strong>
                ₹{amount.toLocaleString()}
              </strong>
            </div>
          )
        )}
      </section>
    </>
  );
}