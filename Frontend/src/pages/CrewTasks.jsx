import { useComplaints } from "../context/ComplaintsContext";
import { useToast } from "../context/ToastContext";
import ComplaintCard from "../components/ComplaintCard";

export default function CrewTasks() {
  const { complaints, updateStatus } = useComplaints();
  const { notify } = useToast();
  const assigned = complaints.filter((c) => c.status === "In Progress");

  const handleComplete = async (id) => {
    const result = await updateStatus(id, "Resolved");
    if (result.success) {
      notify(`Case #${String(id).padStart(4, "0")} marked as resolved`, "success");
    } else {
      notify(result.error || "Couldn't mark case resolved.", "error");
    }
  };

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