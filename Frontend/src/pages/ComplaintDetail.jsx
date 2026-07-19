import { Link, useParams } from "react-router-dom";
import { useComplaints } from "../context/ComplaintsContext";
import { useAuth } from "../context/AuthContext";
import {
  IconArrowRight,
  IconPin,
  IconAlertTriangle,
  IconCheckCircle,
  IconClipboard,
  IconReport,
  IconGrid,
} from "../components/Icons";

const STEPS = ["Pending", "In Progress", "Resolved"];

const backFor = {
  citizen: { to: "/my-complaints", label: "My Complaints", icon: IconClipboard },
  crew: { to: "/crew", label: "Assigned Tasks", icon: IconReport },
  admin: { to: "/dashboard", label: "Dashboard", icon: IconGrid },
};

export default function ComplaintDetail() {
  const { id } = useParams();
  const { complaints } = useComplaints();
  const { user } = useAuth();

  const complaint = complaints.find((c) => String(c.id) === id);
  const back = backFor[user?.role] || { to: "/", label: "Home" };

  if (!complaint) {
    return (
      <div className="page">
        <span className="eyebrow">Not Found</span>
        <h1>Complaint not found</h1>
        <p>This complaint may have been removed or the link is incorrect.</p>
        <Link className="detail-back" to={back.to}>
          {back.icon && <back.icon />} Back to {back.label}
        </Link>
      </div>
    );
  }

  const stepIndex = STEPS.indexOf(complaint.status);

  return (
    <div className="page">
      <Link className="detail-back" to={back.to}>
        {back.icon && <back.icon />} Back to {back.label}
      </Link>

      <span className="case-no">Case No. {String(complaint.id).padStart(4, "0")}</span>
      <div className="detail-header">
        <h1>{complaint.location}</h1>
        <span className={`status-badge ${complaint.status.toLowerCase().replace(" ", "-")}`}>
          {complaint.status}
        </span>
      </div>

      <div className="detail-photo-wrap">
        {complaint.photo ? (
          <img src={complaint.photo} alt="Reported issue" className="detail-photo" />
        ) : (
          <div className="detail-photo detail-photo-empty">No photo attached</div>
        )}
      </div>

      {/* Status timeline */}
      <div className="status-timeline">
        {STEPS.map((step, i) => (
          <div key={step} className={`timeline-step ${i <= stepIndex ? "done" : ""} ${i === stepIndex ? "current" : ""}`}>
            <span className="timeline-dot">{i < stepIndex ? <IconCheckCircle /> : null}</span>
            <span className="timeline-label">{step}</span>
            {i < STEPS.length - 1 && <span className="timeline-line" />}
          </div>
        ))}
      </div>

      <div className="detail-section">
        <h2>Description</h2>
        <p>{complaint.description}</p>
      </div>

      {complaint.hazard && complaint.hazard !== "None" && (
        <p className="hazard-tag"><IconAlertTriangle /> {complaint.hazard}</p>
      )}

      <div className="detail-meta">
        {complaint.reportedBy && <p className="reported-by">Filed by {complaint.reportedBy}</p>}
        <p className="date">Reported: {complaint.createdAt}</p>
      </div>

      {complaint.coords && (
        <a
          className="map-link"
          href={`https://www.google.com/maps?q=${complaint.coords.lat},${complaint.coords.lng}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <IconPin /> View on Map <IconArrowRight />
        </a>
      )}
    </div>
  );
}
