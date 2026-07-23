import { useComplaints } from "../context/ComplaintsContext";
import { useAuth } from "../context/AuthContext";
import ComplaintCard from "../components/ComplaintCard";

export default function MyComplaints() {
  const { complaints } = useComplaints();
  const { user } = useAuth();

  const myComplaints = complaints.filter((c) => c.reportedBy === user?.name);

  return (
    <div className="page">
      <h1>My Complaints</h1>
      {myComplaints.length === 0 ? (
        <p>No complaints submitted yet.</p>
      ) : (
        <div className="complaint-list grid-desktop">
          {myComplaints.map((c) => (
            <ComplaintCard key={c.id} complaint={c} />
          ))}
        </div>
      )}
    </div>
  );
}