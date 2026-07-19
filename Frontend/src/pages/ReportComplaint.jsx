import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useComplaints } from "../context/ComplaintsContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { findPossibleDuplicates } from "../utils/duplicateDetection";
import { IconPin, IconAlertCircle, IconAlertTriangle, IconCamera, IconReport, IconArrowRight } from "../components/Icons";

export default function ReportComplaint() {
  const { complaints, addComplaint } = useComplaints();
  const { user } = useAuth();
  const { notify } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    location: "",
    description: "",
    hazard: "None",
    photo: null,
    coords: null,
  });

  const [locating, setLocating] = useState(false);
  const [locError, setLocError] = useState("");
  const [duplicates, setDuplicates] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (duplicates.length) setDuplicates([]);
  };

  const handlePhoto = (e) => {
    const file = e.target.files[0];
    if (file) {
      setForm((prev) => ({ ...prev, photo: URL.createObjectURL(file) }));
    }
  };

  const handleUseLocation = () => {
    if (!navigator.geolocation) {
      setLocError("Geolocation is not supported by this browser.");
      return;
    }
    setLocating(true);
    setLocError("");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setForm((prev) => ({
          ...prev,
          coords: { lat: latitude, lng: longitude },
          location:
            prev.location || `Lat ${latitude.toFixed(5)}, Lng ${longitude.toFixed(5)}`,
        }));
        setLocating(false);
      },
      (error) => {
        setLocError(
          error.code === error.PERMISSION_DENIED
            ? "Location permission denied. Enter the location manually."
            : "Couldn't fetch your location. Enter it manually."
        );
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const submitComplaint = async () => {
    await addComplaint({ ...form, reportedBy: user?.name });
    notify("Complaint submitted successfully", "success");
    navigate("/my-complaints");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.location || !form.description) return;

    const matches = findPossibleDuplicates(form, complaints);
    if (matches.length) {
      setDuplicates(matches);
      return;
    }
    await submitComplaint();
  };

  const handleSubmitAnyway = async () => {
    setDuplicates([]);
    await submitComplaint();
  };

  return (
    <div className="page">
      <span className="eyebrow">New Incident</span>
      <h1>Report a Garbage Issue</h1>
      <form onSubmit={handleSubmit} className="complaint-form">
        <div className="location-row">
          <div className="field-group">
            <label htmlFor="location">Location</label>
            <input
              id="location"
              name="location"
              value={form.location}
              onChange={handleChange}
              placeholder="e.g. MG Road, Near Bus Stop"
              required
            />
          </div>
          <button
            type="button"
            className="gps-btn"
            onClick={handleUseLocation}
            disabled={locating}
          >
            <IconPin /> {locating ? "Locating..." : "Use My Location"}
          </button>
        </div>

        {form.coords && (
          <p className="coords-preview">
            <IconPin /> GPS captured: {form.coords.lat.toFixed(5)}, {form.coords.lng.toFixed(5)}
          </p>
        )}
        {locError && <p className="loc-error"><IconAlertCircle /> {locError}</p>}

        <label>
          Description
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Describe the issue"
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

        <label>
          <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><IconCamera /> Upload Photo</span>
          <input type="file" accept="image/*" onChange={handlePhoto} />
        </label>

        {form.photo && (
          <img src={form.photo} alt="preview" className="photo-preview" />
        )}

        {duplicates.length > 0 && (
          <div className="duplicate-warning">
            <p className="duplicate-warning-title">
              <IconAlertTriangle /> This looks similar to {duplicates.length === 1 ? "an existing report" : "existing reports"}
            </p>
            <ul className="duplicate-list">
              {duplicates.slice(0, 3).map(({ complaint }) => (
                <li key={complaint.id}>
                  <Link to={`/complaint/${complaint.id}`} target="_blank" rel="noopener noreferrer">
                    Case #{String(complaint.id).padStart(4, "0")} — {complaint.location}
                    <IconArrowRight />
                  </Link>
                  <span className={`status-badge ${complaint.status.toLowerCase().replace(" ", "-")}`}>
                    {complaint.status}
                  </span>
                </li>
              ))}
            </ul>
            <div className="duplicate-actions">
              <button type="button" className="secondary-btn" onClick={() => setDuplicates([])}>
                Let me edit
              </button>
              <button type="button" className="edit-btn" onClick={handleSubmitAnyway}>
                Submit Anyway
              </button>
            </div>
          </div>
        )}

        <button type="submit"><IconReport /> Submit Complaint</button>
      </form>
    </div>
  );
}