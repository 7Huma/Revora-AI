export default function RiskCard({ title, value }) {
  return (
    <div className="metric-card risk">
      <span>{title}</span>
      <strong>{value}</strong>
    </div>
  );
}
