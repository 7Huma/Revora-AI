import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function RevenueChart({ data }) {
  const chart = (data || []).map((x) => ({
    name: `#${String(x.id).slice(0, 8)}`,
    amount: Number(x.amount_at_risk || x.amount || 0),
  }));

  return (
    <div className="chart panel">
      <div className="panel-header">
        <h2>Revenue at Risk</h2>
      </div>

      {chart.length === 0 ? (
        <div className="empty">No revenue data available.</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={chart}
            margin={{
              top: 10,
              right: 20,
              left: 10,
              bottom: 10,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis
              dataKey="name"
              tick={{ fontSize: 11 }}
            />

            <YAxis
              tick={{ fontSize: 11 }}
              tickFormatter={(value) =>
                `₹${Number(value).toLocaleString()}`
              }
            />

            <Tooltip
              formatter={(value) =>
                `₹${Number(value).toLocaleString()}`
              }
            />

            <Bar
              dataKey="amount"
              name="Revenue at Risk"
              radius={[5, 5, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}