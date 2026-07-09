import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useComplaints } from "../context/ComplaintsContext";
import { useAuth } from "../context/AuthContext";

export default function ReportComplaint() {
  const { addComplaint } = useComplaints();
  const { user } = useAuth();
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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
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

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.location || !form.description) return;
    addComplaint({ ...form, reportedBy: user?.name });
    navigate("/my-complaints");
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
            {locating ? "Locating..." : "📍 Use My Location"}
          </button>
        </div>

        {form.coords && (
          <p className="coords-preview">
            GPS captured: {form.coords.lat.toFixed(5)}, {form.coords.lng.toFixed(5)}
          </p>
        )}
        {locError && <p className="loc-error">{locError}</p>}

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
          Upload Photo
          <input type="file" accept="image/*" onChange={handlePhoto} />
        </label>

        {form.photo && (
          <img src={form.photo} alt="preview" className="photo-preview" />
        )}

        <button type="submit">Submit Complaint</button>
      </form>
    </div>
  );
}