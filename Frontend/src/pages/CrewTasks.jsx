import { useComplaints } from "../context/ComplaintsContext";
import ComplaintCard from "../components/ComplaintCard";

export default function CrewTasks() {
  const { complaints, updateStatus } = useComplaints();
  const assigned = complaints.filter((c) => c.status === "In Progress");

  const handleComplete = (id) => updateStatus(id, "Resolved");

  return (
    <div className="page">
      <span className="eyebrow">Cleanup Crew</span>
      <h1>Assigned Tasks</h1>
      {assigned.length === 0 ? (
        <p>No tasks assigned right now. Check back after the supervisor assigns a case.</p>
      ) : (
        <div className="complaint-list grid-desktop">
          {assigned.map((c) => (
            <ComplaintCard key={c.id} complaint={c} onComplete={handleComplete} />
          ))}
        </div>
      )}
    </div>
  );
}