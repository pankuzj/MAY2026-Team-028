import { useState } from "react";
import { useOperational } from "../context/OperationalContext";
import { useComplaints } from "../context/ComplaintsContext";
import { useToast } from "../context/ToastContext";
import { IconTruck, IconUsers, IconSearch, IconPlus, IconRadar, IconX, IconCheckCircle, IconAlertTriangle } from "../components/Icons";

export default function VehicleAssignment() {
  const { vehicles, updateVehicleStatus, addVehicle } = useOperational();
  const { complaints } = useComplaints();
  const { notify } = useToast();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  // Modal State
  const [showAddVehicleModal, setShowAddVehicleModal] = useState(false);
  const [assigningVehicle, setAssigningVehicle] = useState(null);

  const [newV, setNewV] = useState({
    plateNo: "",
    model: "Electric Tipper Truck",
    type: "Mini Tipper",
    capacity: "3.0 Tons",
    ward: "Indiranagar (Ward 12)",
    driver: "Unassigned",
  });

  // Calculate Metrics
  const totalEnRoute = vehicles.filter((v) => v.status === "En Route" || v.status === "On Site").length;
  const totalAvailable = vehicles.filter((v) => v.status === "Available").length;
  const totalMaintenance = vehicles.filter((v) => v.status === "Maintenance").length;

  // Filtered List
  const filteredVehicles = vehicles.filter((v) => {
    const q = search.trim().toLowerCase();
    const matchesSearch =
      !q ||
      v.plateNo.toLowerCase().includes(q) ||
      v.model.toLowerCase().includes(q) ||
      v.driver.toLowerCase().includes(q) ||
      v.ward.toLowerCase().includes(q) ||
      v.type.toLowerCase().includes(q);
    const matchesStatus = statusFilter === "All" || v.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleCreateVehicle = (e) => {
    e.preventDefault();
    if (!newV.plateNo) {
      notify("Please provide license plate number.", "error");
      return;
    }
    addVehicle(newV);
    notify(`Vehicle ${newV.plateNo} registered in municipal fleet!`, "success");
    setNewV({
      plateNo: "",
      model: "Electric Tipper Truck",
      type: "Mini Tipper",
      capacity: "3.0 Tons",
      ward: "Indiranagar (Ward 12)",
      driver: "Unassigned",
    });
    setShowAddVehicleModal(false);
  };

  const handleSaveAssignment = (e) => {
    e.preventDefault();
    if (!assigningVehicle) return;
    updateVehicleStatus(
      assigningVehicle.id,
      assigningVehicle.status,
      assigningVehicle.driver,
      assigningVehicle.assignedTask,
      assigningVehicle.ward
    );
    notify(`Vehicle dispatch updated for ${assigningVehicle.plateNo}`, "success");
    setAssigningVehicle(null);
  };

  return (
    <div className="page page-wide">
      <div className="page-header">
        <div>
          <span className="eyebrow">Fleet Management</span>
          <h1>Vehicle & Fleet Assignment</h1>
          <p className="page-lead">
            Track, dispatch, and assign waste compactors, mini tippers, and sweeping vehicles across active sanitation zones.
          </p>
        </div>
        <div className="page-actions">
          <button className="primary-btn" onClick={() => setShowAddVehicleModal(true)}>
            <IconPlus /> Register Vehicle
          </button>
        </div>
      </div>

      {/* KPI Overview Banner */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon accent"><IconTruck /></div>
          <div>
            <span className="kpi-value">{totalEnRoute} / {vehicles.length}</span>
            <span className="kpi-label">Active Dispatched</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon green"><IconCheckCircle /></div>
          <div>
            <span className="kpi-value">{totalAvailable}</span>
            <span className="kpi-label">Available Fleet</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon blue"><IconRadar /></div>
          <div>
            <span className="kpi-value">Live GPS</span>
            <span className="kpi-label">Telemetry Active</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon amber"><IconAlertTriangle /></div>
          <div>
            <span className="kpi-value">{totalMaintenance}</span>
            <span className="kpi-label">Depot Maintenance</span>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="dashboard-toolbar">
        <div className="search-wrap">
          <IconSearch />
          <input
            type="text"
            className="search-input"
            placeholder="Search by license plate, vehicle model, driver, or ward..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="search-clear-btn" onClick={() => setSearch("")}>
              <IconX />
            </button>
          )}
        </div>
        <div className="filters">
          {["All", "En Route", "On Site", "Available", "In Depot", "Maintenance"].map((st) => (
            <button
              key={st}
              className={statusFilter === st ? "active" : ""}
              onClick={() => setStatusFilter(st)}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Vehicle Grid */}
      <div className="card-grid">
        {filteredVehicles.length === 0 ? (
          <div className="empty-state">No fleet vehicles match your search query.</div>
        ) : (
          filteredVehicles.map((v) => (
            <div key={v.id} className="op-card fleet-card">
              <div className="op-card-header">
                <div className="fleet-badge-wrap">
                  <span className="op-id">{v.id}</span>
                  <h3 className="op-title">{v.plateNo}</h3>
                  <span className="op-subtitle">{v.model}</span>
                </div>
                <span className={`op-status-badge status-${v.status.toLowerCase().replace(" ", "-")}`}>
                  {v.status}
                </span>
              </div>

              <div className="op-card-body">
                {/* Fuel/Battery Level Indicator */}
                <div className="fuel-bar-wrap">
                  <div className="fuel-label">
                    <span>Fuel / Charge Level:</span>
                    <span className="font-bold">{v.fuelLevel}%</span>
                  </div>
                  <div className="fuel-track">
                    <div
                      className={`fuel-fill ${v.fuelLevel < 35 ? "low" : ""}`}
                      style={{ width: `${v.fuelLevel}%` }}
                    />
                  </div>
                </div>

                <div className="op-detail-row">
                  <span className="label">Driver & Crew:</span>
                  <span className="value font-bold">{v.driver}</span>
                </div>

                <div className="op-detail-row">
                  <span className="label">Zone / Ward:</span>
                  <span className="value">{v.ward}</span>
                </div>

                <div className="op-detail-row">
                  <span className="label">Assigned Task:</span>
                  <span className="value tag">{v.assignedTask}</span>
                </div>

                <div className="op-detail-row">
                  <span className="label">Payload Capacity:</span>
                  <span className="value">{v.capacity}</span>
                </div>
              </div>

              <div className="op-card-footer">
                <button
                  className="primary-btn btn-sm"
                  onClick={() => setAssigningVehicle({ ...v })}
                >
                  Dispatch / Assign
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Live Fleet Tracking Radar Banner */}
      <div className="live-radar-box">
        <div className="radar-head">
          <IconRadar className="radar-spin-icon" />
          <div>
            <h4>Live Municipal Fleet Telemetry</h4>
            <p>Real-time GPS dispatch & automated payload routing active across Ward 04, Ward 08, & Ward 12.</p>
          </div>
        </div>
        <div className="radar-pills">
          <span className="pill green">● KA-01-EA-4821 [Speed: 24 km/h]</span>
          <span className="pill blue">● KA-01-EV-9012 [On Site - Compacting]</span>
          <span className="pill accent">● KA-05-MS-1104 [Depot Ready]</span>
        </div>
      </div>

      {/* MODAL: Register Vehicle */}
      {showAddVehicleModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Register New Vehicle</h2>
              <button className="icon-btn" onClick={() => setShowAddVehicleModal(false)}><IconX /></button>
            </div>
            <form onSubmit={handleCreateVehicle} className="complaint-form">
              <label>
                License Plate Number
                <input
                  type="text"
                  required
                  placeholder="e.g. KA-01-EV-2026"
                  value={newV.plateNo}
                  onChange={(e) => setNewV({ ...newV, plateNo: e.target.value })}
                />
              </label>
              <label>
                Vehicle Type
                <select
                  value={newV.type}
                  onChange={(e) => setNewV({ ...newV, type: e.target.value })}
                >
                  <option value="Mini Tipper">Mini Tipper</option>
                  <option value="Compactor">Heavy Compactor Truck</option>
                  <option value="Road Sweeper">Mechanical Road Sweeper</option>
                  <option value="Inspection Van">Inspection Van</option>
                  <option value="Hazmat Van">Biohazard Transporter</option>
                </select>
              </label>
              <label>
                Model Name
                <input
                  type="text"
                  required
                  placeholder="e.g. Electric Heavy Duty Sweeper"
                  value={newV.model}
                  onChange={(e) => setNewV({ ...newV, model: e.target.value })}
                />
              </label>
              <label>
                Payload Capacity
                <input
                  type="text"
                  required
                  placeholder="e.g. 4.5 Tons"
                  value={newV.capacity}
                  onChange={(e) => setNewV({ ...newV, capacity: e.target.value })}
                />
              </label>
              <label>
                Assigned Ward
                <input
                  type="text"
                  required
                  placeholder="e.g. Indiranagar (Ward 12)"
                  value={newV.ward}
                  onChange={(e) => setNewV({ ...newV, ward: e.target.value })}
                />
              </label>
              <label>
                Assigned Driver / Lead
                <input
                  type="text"
                  placeholder="e.g. Suresh Patil"
                  value={newV.driver}
                  onChange={(e) => setNewV({ ...newV, driver: e.target.value })}
                />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddVehicleModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Register to Fleet</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Dispatch / Reassign Vehicle */}
      {assigningVehicle && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Dispatch Vehicle: {assigningVehicle.plateNo}</h2>
              <button className="icon-btn" onClick={() => setAssigningVehicle(null)}><IconX /></button>
            </div>
            <form onSubmit={handleSaveAssignment} className="complaint-form">
              <label>
                Dispatch Status
                <select
                  value={assigningVehicle.status}
                  onChange={(e) => setAssigningVehicle({ ...assigningVehicle, status: e.target.value })}
                >
                  <option value="En Route">En Route</option>
                  <option value="On Site">On Site</option>
                  <option value="Available">Available</option>
                  <option value="In Depot">In Depot</option>
                  <option value="Maintenance">Maintenance</option>
                </select>
              </label>
              <label>
                Driver & Crew Lead
                <input
                  type="text"
                  value={assigningVehicle.driver}
                  onChange={(e) => setAssigningVehicle({ ...assigningVehicle, driver: e.target.value })}
                />
              </label>
              <label>
                Target Route / Ward
                <input
                  type="text"
                  value={assigningVehicle.ward}
                  onChange={(e) => setAssigningVehicle({ ...assigningVehicle, ward: e.target.value })}
                />
              </label>
              <label>
                Assigned Task / Case Reference
                <select
                  value={assigningVehicle.assignedTask}
                  onChange={(e) => setAssigningVehicle({ ...assigningVehicle, assignedTask: e.target.value })}
                >
                  <option value="Standby at Central Depot">Standby at Central Depot</option>
                  {complaints.map((c) => (
                    <option key={c.id} value={`Case #${String(c.id).padStart(4, "0")} (${c.location})`}>
                      Case #{String(c.id).padStart(4, "0")} - {c.location} [{c.status}]
                    </option>
                  ))}
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setAssigningVehicle(null)}>Cancel</button>
                <button type="submit" className="primary-btn">Save & Dispatch</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
