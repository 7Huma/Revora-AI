import { useEffect, useState } from "react";
import { api } from "../services/api";
import RevenueCard from "../components/RevenueCard";
import RiskCard from "../components/RiskCard";
import RecoveryCases from "../components/RecoveryCases";
import RevenueChart from "../components/RevenueChart";

export default function Dashboard({ page }) {
  const [summary, setSummary] = useState(null);
  const [cases, setCases] = useState([]);
  const [error, setError] = useState("");

  // ==========================================
  // LOAD DASHBOARD DATA
  // ==========================================

  const load = async () => {
    try {
      setError("");

      const [summaryData, casesData] = await Promise.all([
        api.summary(),
        api.cases(),
      ]);

      setSummary(summaryData);
      setCases(casesData);
    } catch (e) {
      console.error(e);
      setError(
        "Backend is not running. Start FastAPI on port 8000."
      );
    }
  };

  // ==========================================
  // RESET DEMO
  // ==========================================

  const resetDemo = async () => {
    try {
      setError("");

      await api.resetDemo();

      await load();
    } catch (e) {
      console.error(e);
      setError("Demo reset failed.");
    }
  };

  // ==========================================
  // INITIAL LOAD
  // ==========================================

  useEffect(() => {
    load();
  }, []);

  // ==========================================
  // ACTIVE CASES
  // ==========================================

  const activeCases = cases.filter((c) => {
    const status = String(
      c.status || ""
    ).toLowerCase();

    return (
      status === "open" ||
      status === "in_progress"
    );
  });

  // ==========================================
  // ANALYTICS PAGE
  // ==========================================

  if (page === "analytics") {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              Revora AI
            </p>

            <h1>Analytics</h1>

            <p className="subtitle">
              Understand where revenue is being recovered.
            </p>
          </div>

          <div className="header-actions">
            <button
              className="demo-reset"
              onClick={resetDemo}
            >
              Reset Demo
            </button>

            <button
              className="refresh"
              onClick={load}
            >
              Refresh
            </button>
          </div>
        </header>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <section className="panel">
          <div className="panel-header">
            <h2>
              Recovery Analytics
            </h2>

            <span>
              {cases.length} total cases
            </span>
          </div>

          <RevenueChart data={cases} />
        </section>
      </>
    );
  }

  // ==========================================
  // RECOVERY CASES PAGE
  // ==========================================

  if (page === "cases") {
    return (
      <>
        <header>
          <div>
            <p className="eyebrow">
              Revora AI
            </p>

            <h1>
              Recovery Cases
            </h1>

            <p className="subtitle">
              Review, diagnose and recover at-risk revenue.
            </p>
          </div>

          <div className="header-actions">
            <button
              className="demo-reset"
              onClick={resetDemo}
            >
              Reset Demo
            </button>

            <button
              className="refresh"
              onClick={load}
            >
              Refresh
            </button>
          </div>
        </header>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <section className="metrics">
          <RevenueCard
            title="Revenue at Risk"
            value={`₹${Number(
              summary?.revenue_at_risk ?? 0
            ).toLocaleString()}`}
          />

          <RevenueCard
            title="Recovered Revenue"
            value={`₹${Number(
              summary?.recovered_revenue ?? 0
            ).toLocaleString()}`}
          />

          <RiskCard
            title="Active Cases"
            value={
              summary?.active_cases ??
              activeCases.length
            }
          />

          <RiskCard
            title="Cases"
            value={cases.length}
          />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Recovery Queue
              </h2>

              <p className="subtitle">
                {activeCases.length} active cases requiring attention
              </p>
            </div>

            <span>
              {activeCases.length} active
            </span>
          </div>

          <RecoveryCases
            cases={cases}
            onExecuted={load}
          />
        </section>
      </>
    );
  }

  // ==========================================
  // MAIN DASHBOARD
  // ==========================================

  return (
    <>
      <header>
        <div>
          <p className="eyebrow">
            Revora AI
          </p>

          <h1>
            Find revenue that's slipping away.
          </h1>

          <p className="subtitle">
            Detect. Diagnose. Recover.
          </p>
        </div>

        <button
          className="demo-reset"
          onClick={resetDemo}
        >
          Reset Demo
        </button>
      </header>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {/* ======================================
          DASHBOARD METRICS
          ====================================== */}

      <section className="metrics">

        <RevenueCard
          title="Revenue at Risk"
          value={`₹${Number(
            summary?.revenue_at_risk ?? 0
          ).toLocaleString()}`}
        />

        <RevenueCard
          title="Recovered Revenue"
          value={`₹${Number(
            summary?.recovered_revenue ?? 0
          ).toLocaleString()}`}
        />

        <RevenueCard
          title="Expected Recovery"
          value={`₹${Number(
            summary?.expected_recovery ?? 0
          ).toLocaleString()}`}
        />

        <RiskCard
          title="Active Cases"
          value={
            summary?.active_cases ??
            activeCases.length
          }
        />

      </section>

      {/* ======================================
          RECOVERY PIPELINE
          ====================================== */}

      <section className="panel">

        <div className="panel-header">

          <h2>
            Revenue Recovery Pipeline
          </h2>

          <span>
            {activeCases.length} active cases
          </span>

        </div>

        <RecoveryCases
          cases={cases}
          onExecuted={load}
        />

      </section>

      {/* ======================================
          REVENUE CHART
          ====================================== */}

      <RevenueChart
        data={cases}
      />
    </>
  );
}