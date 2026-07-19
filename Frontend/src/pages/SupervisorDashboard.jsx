import { useState } from "react";
import { useComplaints } from "../context/ComplaintsContext";
import { useToast } from "../context/ToastContext";
import { getDuplicateMatches } from "../utils/duplicateDetection";
import ComplaintCard from "../components/ComplaintCard";

export default function SupervisorDashboard() {
  const { complaints, updateStatus } = useComplaints();
  const { notify } = useToast();
  const [filter, setFilter] = useState("All");

  const filtered =
    filter === "All" ? complaints : complaints.filter((c) => c.status === filter);

  const handleAssign = async (id) => {
    const complaint = complaints.find((c) => c.id === id);
    const dupes = complaint ? getDuplicateMatches(complaint, complaints) : [];
    if (dupes.length) {
      const caseList = dupes
        .map((m) => `#${String(m.complaint.id).padStart(4, "0")}`)
        .join(", ");
      const proceed = window.confirm(
        `This looks like a possible duplicate of case ${caseList}. Assign crew anyway?`
      );
      if (!proceed) return;
    }

    const result = await updateStatus(id, "In Progress");
    if (result.success) {
      notify(`Crew assigned to case #${String(id).padStart(4, "0")}`, "success");
    } else {
      notify(result.error || "Couldn't assign crew.", "error");
    }
  };

  return (
    <div className="page">
      <h1>Supervisor Dashboard</h1>
      <div className="filters">
        {["All", "Pending", "In Progress", "Resolved"].map((f) => (
          <button
            key={f}
            className={filter === f ? "active" : ""}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>
      <div className="complaint-list grid-desktop">
        {filtered.map((c) => (
          <ComplaintCard
            key={c.id}
            complaint={c}
            onAssign={handleAssign}
            duplicatesOf={getDuplicateMatches(c, complaints)}
          />
        ))}
      </div>
    </div>
  );
}