const API =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

async function get(path) {
  const response = await fetch(
    `${API}${path}`
  );

  if (!response.ok) {
    throw new Error(
      await response.text()
    );
  }

  return response.json();
}

async function post(
  path,
  body = {}
) {
  const response = await fetch(
    `${API}${path}`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    throw new Error(
      await response.text()
    );
  }

  return response.json();
}

export const api = {
  // ============================================================
  // DASHBOARD
  // ============================================================

  summary: () =>
    get("/dashboard/summary"),

  risk: () =>
    get("/dashboard/revenue-at-risk"),

  // ============================================================
  // RECOVERY CASES
  // ============================================================

  cases: () =>
    get("/recovery/cases"),

  // Get one specific case.
  // Used by the AI drawer after execution.
  getCase: (id) =>
    get(`/recovery/cases/${id}`),

  // Execute recovery intervention.
  execute: (id, channel = null) =>
    post(
      `/recovery/execute/${id}`,
      channel
        ? { channel }
        : {}
    ),
  
    autonomousRecovery: (id) =>
  post(
    `/recovery/autonomous/${id}`
  ),
  // ============================================================
  // AI DRAWER
  // ============================================================

  interventionHistory: (id) =>
    get(
      `/recovery/cases/${id}/interventions`
    ),

  // ============================================================
  // DEMO
  // ============================================================

  resetDemo: () =>
    post("/recovery/demo/reset"),
};