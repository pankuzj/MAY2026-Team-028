import { useState } from "react";
import { IconX, IconUserPlus, IconTool, IconTruck } from "./Icons";

// Fixed rosters for the mock data phase. These map 1:1 to what the
// eventual `GET /crews`, `GET /equipment`, `GET /vehicles` endpoints would
// return, so swapping this for fetched options later is a data-source
// change, not a form-shape change.
const CREWS = ["Team Alpha", "Team Bravo", "Team Charlie", "Team Delta"];

const EQUIPMENT_OPTIONS = [
  "Truck-Mounted Compactor",
  "Manual Loader",
  "Disinfectant Sprayer",
  "Protective Gear",
  "Shovels & Rakes",
];

// #12 — vehicle assignment dropdown, bolted onto this same modal rather
// than a separate form, since a vehicle is just one more field on the
// same allocation record.
const VEHICLES = [
  "KA-01 AB 1234 — Compactor Truck",
  "KA-01 CD 5678 — Mini Tipper",
  "KA-01 EF 9012 — Tricycle Loader",
  "KA-01 GH 3456 — Pickup Van",
];

const emptyForm = { crew: "", workerCount: 2, equipment: [], vehicle: "" };

export default function AssignCrewModal({ complaint, onClose, onSubmit }) {
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const toggleEquipment = (item) =>
    setForm((prev) => ({
      ...prev,
      equipment: prev.equipment.includes(item)
        ? prev.equipment.filter((e) => e !== item)
        : [...prev.equipment, item],
    }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.crew || !form.vehicle) {
      setError("Select a crew and a vehicle before assigning.");
      return;
    }
    setError("");
    setSubmitting(true);
    const result = await onSubmit(form);
    setSubmitting(false);
    if (!result.success) {
      setError(result.error || "Couldn't assign crew. Try again.");
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assign-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 id="assign-modal-title">
            <IconUserPlus /> Assign Crew — Case #{String(complaint.id).padStart(4, "0")}
          </h2>
          <button type="button" className="modal-close-btn" onClick={onClose} aria-label="Close">
            <IconX />
          </button>
        </div>

        <p className="modal-subtitle">{complaint.location}</p>

        <form onSubmit={handleSubmit} className="complaint-form modal-form">
          <label>
            Crew
            <select
              value={form.crew}
              onChange={(e) => setForm((prev) => ({ ...prev, crew: e.target.value }))}
            >
              <option value="">Select a crew...</option>
              {CREWS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>

          <label>
            Workers Needed
            <input
              type="number"
              min={1}
              max={12}
              value={form.workerCount}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, workerCount: Number(e.target.value) }))
              }
            />
          </label>

          <fieldset className="equipment-fieldset">
            <legend>
              <IconTool /> Equipment
            </legend>
            <div className="equipment-grid">
              {EQUIPMENT_OPTIONS.map((item) => (
                <label key={item} className="checkbox-field">
                  <input
                    type="checkbox"
                    checked={form.equipment.includes(item)}
                    onChange={() => toggleEquipment(item)}
                  />
                  {item}
                </label>
              ))}
            </div>
          </fieldset>

          <label>
            <IconTruck /> Vehicle
            <select
              value={form.vehicle}
              onChange={(e) => setForm((prev) => ({ ...prev, vehicle: e.target.value }))}
            >
              <option value="">Select a vehicle...</option>
              {VEHICLES.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </label>

          {error && <p className="loc-error">{error}</p>}

          <div className="detail-actions">
            <button type="submit" className="save-btn" disabled={submitting}>
              {submitting ? "Assigning..." : "Assign Crew"}
            </button>
            <button type="button" className="secondary-btn" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
