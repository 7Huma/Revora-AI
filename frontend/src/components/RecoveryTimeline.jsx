export default function RecoveryTimeline({ events = [] }) {
  return (
    <div className="timeline">
      {events.map((event, i) => (
        <div className="timeline-item" key={i}>
          <span>{event.time}</span>
          <p>{event.label}</p>
        </div>
      ))}
    </div>
  );
}
