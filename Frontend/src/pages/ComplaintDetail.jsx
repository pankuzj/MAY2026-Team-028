import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useComplaints } from "../context/ComplaintsContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import {
  IconArrowRight,
  IconPin,
  IconAlertTriangle,
  IconAlertCircle,
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
  const { complaints, updateComplaint, cancelComplaint } = useComplaints();
  const { user } = useAuth();
  const { notify } = useToast();
  const navigate = useNavigate();

  const complaint = complaints.find((c) => String(c.id) === id);
  const back = backFor[user?.role] || { to: "/", label: "Home" };

  // Only the citizen who filed it may edit/withdraw it, and only while
  // it's still Pending — once a crew touches it, changes should go
  // through the crew/admin flow instead.
  const canManage =
    user?.role === "citizen" &&
    complaint?.reportedBy === user?.name &&
    complaint?.status === "Pending";

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState(null);
  const [error, setError] = useState("");
  const [cancelling, setCancelling] = useState(false);

  const startEditing = () => {
    setForm({
      location: complaint.location,
      description: complaint.description,
      hazard: complaint.hazard || "None",
    });
    setError("");
    setEditing(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.location || !form.description) return;
    const result = await updateComplaint(complaint.id, form);
    if (result.success) {
      setEditing(false);
      notify("Changes saved", "success");
    } else {
      const msg = result.error || "Couldn't save changes. Try again.";
      setError(msg);
      notify(msg, "error");
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Withdraw this complaint? This can't be undone.")) return;
    setCancelling(true);
    const result = await cancelComplaint(complaint.id);
    setCancelling(false);
    if (result.success) {
      notify("Complaint withdrawn", "info");
      navigate(back.to);
    } else {
      const msg = result.error || "Couldn't withdraw this complaint.";
      setError(msg);
      notify(msg, "error");
    }
  };

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

      {error && <p className="loc-error"><IconAlertCircle /> {error}</p>}

      {editing ? (
        <form onSubmit={handleSave} className="complaint-form">
          <label>
            Location
            <input
              name="location"
              value={form.location}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Description
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Hazard Type
            <select name="hazard" value={form.hazard} onChange={handleChange}>
              <option>None</option>
              <option>Foul Smell</option>
              <option>Overflowing Bin</option>
              <option>Mosquito Breeding</option>
              <option>Risk to Children</option>
            </select>
          </label>

          <div className="detail-actions">
            <button type="submit" className="save-btn">
              <IconCheckCircle /> Save Changes
            </button>
            <button type="button" className="secondary-btn" onClick={() => setEditing(false)}>
              Discard
            </button>
          </div>
        </form>
      ) : (
        <>
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

          {canManage && (
            <div className="detail-actions">
              <button type="button" className="edit-btn" onClick={startEditing}>
                Edit Complaint
              </button>
              <button
                type="button"
                className="cancel-btn"
                onClick={handleCancel}
                disabled={cancelling}
              >
                {cancelling ? "Withdrawing..." : "Withdraw Complaint"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}