import { useEffect, useState } from "react";
import { api } from "../services/api";
import RecoveryCases from "../components/RecoveryCases";
import RevenueCard from "../components/RevenueCard";
import RiskCard from "../components/RiskCard";

export default function RecoveryCasesPage() {
  const [summary, setSummary] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [resetting, setResetting] = useState(false);

  const load = async () => {
    try {
      setLoading(true);

      const [summaryData, casesData] = await Promise.all([
        api.summary(),
        api.cases(),
      ]);

      setSummary(summaryData);
      setCases(casesData);
      setError("");
    } catch (e) {
      console.error(e);
      setError("Unable to load recovery cases.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleReset = async () => {
    try {
      setResetting(true);
      setError("");

      await api.resetDemo();

      await load();
    } catch (e) {
      console.error(e);
      setError("Unable to reset demo.");
    } finally {
      setResetting(false);
    }
  };

  const activeCases = cases.filter(
    (c) =>
      String(c.status || "").toLowerCase() !== "recovered"
  );

  const recoveredCases = cases.filter(
    (c) =>
      String(c.status || "").toLowerCase() === "recovered"
  );

  return (
    <>
      <header>
        <div>
          <p className="eyebrow">Revora AI</p>

          <h1>Recovery Cases</h1>

          <p className="subtitle">
            Review, diagnose and recover at-risk revenue.
          </p>
        </div>

        <div className="header-actions">
          <button
            className="demo-reset"
            onClick={handleReset}
            disabled={resetting}
          >
            {resetting ? "Resetting..." : "Reset Demo"}
          </button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="empty">
          Loading recovery cases...
        </div>
      ) : (
        <>
          <section className="metrics">
            <RevenueCard
              title="Revenue at Risk"
              value={`₹${(
                summary?.revenue_at_risk ?? 0
              ).toLocaleString()}`}
            />

            <RevenueCard
              title="Recovered Revenue"
              value={`₹${(
                summary?.recovered_revenue ?? 0
              ).toLocaleString()}`}
            />

            <RiskCard
              title="Active Cases"
              value={activeCases.length}
            />

            <RiskCard
              title="Recovered Cases"
              value={recoveredCases.length}
            />
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <h2>Recovery Queue</h2>

                <p className="panel-subtitle">
                  {activeCases.length} active cases requiring attention
                </p>
              </div>

              <span>
                {activeCases.length} active
              </span>
            </div>

            {activeCases.length === 0 ? (
              <div className="empty">
                No active recovery cases.
              </div>
            ) : (
              <RecoveryCases
                cases={activeCases}
                onExecuted={load}
              />
            )}
          </section>

          {recoveredCases.length > 0 && (
            <section className="panel recovered-panel">
              <div className="panel-header">
                <div>
                  <h2>Recovery History</h2>

                  <p className="panel-subtitle">
                    Successfully recovered cases
                  </p>
                </div>

                <span>
                  {recoveredCases.length} recovered
                </span>
              </div>

              <RecoveryCases
                cases={recoveredCases}
                onExecuted={load}
              />
            </section>
          )}
        </>
      )}
    </>
  );
}