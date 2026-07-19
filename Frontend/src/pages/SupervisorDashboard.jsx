import { useState } from "react";
import { useComplaints } from "../context/ComplaintsContext";
import ComplaintCard from "../components/ComplaintCard";

export default function SupervisorDashboard() {
  const { complaints, updateStatus } = useComplaints();
  const [filter, setFilter] = useState("All");

  const filtered =
    filter === "All" ? complaints : complaints.filter((c) => c.status === filter);

  const handleAssign = (id) => {
    updateStatus(id, "In Progress");
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
          <ComplaintCard key={c.id} complaint={c} onAssign={handleAssign} />
        ))}
      </div>
    </div>
  );
}