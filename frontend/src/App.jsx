import { useState } from "react";
import Analytics from "./pages/Analytics";
import Dashboard from "./pages/Dashboard";
import RecoveryCasesPage from "./pages/RecoveryCasesPage";

export default function App() {
  const [page, setPage] = useState("dashboard");

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          Revora <span>AI</span>
        </div>

        <nav>
          <button
            className={page === "dashboard" ? "active" : ""}
            onClick={() => setPage("dashboard")}
          >
            Dashboard
          </button>

          <button
            className={page === "cases" ? "active" : ""}
            onClick={() => setPage("cases")}
          >
            Recovery Cases
          </button>

          <button
            className={page === "analytics" ? "active" : ""}
            onClick={() => setPage("analytics")}
          >
            Analytics
          </button>
        </nav>
      </aside>

      <main className="content">

        {page === "dashboard" && (
          <Dashboard />
        )}

        {page === "cases" && (
          <RecoveryCasesPage />
        )}

        {page === "analytics" && (
          <Analytics />
        )}

      </main>
    </div>
  );
}