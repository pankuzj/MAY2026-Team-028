import { useMemo, useState } from "react";
import { useComplaints } from "../context/ComplaintsContext";
import { useToast } from "../context/ToastContext";
import { getDuplicateMatches } from "../utils/duplicateDetection";
import ComplaintCard from "../components/ComplaintCard";
import AssignCrewModal from "../components/AssignCrewModal";
import { IconSearch, IconSliders, IconX } from "../components/Icons";

// Kept in sync with the hazard options offered on ReportComplaint /
// ComplaintDetail's edit form — "None" is intentionally left out of the
// filter list since filtering for "no hazard" isn't a useful admin query.
const HAZARD_TYPES = [
  "Foul Smell",
  "Overflowing Bin",
  "Mosquito Breeding",
  "Risk to Children",
];

const SORT_OPTIONS = [
  { value: "newest", label: "Newest First" },
  { value: "oldest", label: "Oldest First" },
];

const DEFAULT_ADVANCED = {
  hazard: "All",
  needsHelpOnly: false,
  dateFrom: "",
  dateTo: "",
  sortBy: "newest",
};

export default function SupervisorDashboard() {
  const { complaints, updateComplaint } = useComplaints();
  const { notify } = useToast();
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [advanced, setAdvanced] = useState(DEFAULT_ADVANCED);
  // Case currently open in the Workforce & Equipment Allocation modal
  // (#11) — null means the modal is closed.
  const [assigningId, setAssigningId] = useState(null);

  const advancedActive =
    advanced.hazard !== "All" ||
    advanced.needsHelpOnly ||
    advanced.dateFrom ||
    advanced.dateTo ||
    advanced.sortBy !== "newest";

  const handleAdvancedChange = (field, value) =>
    setAdvanced((prev) => ({ ...prev, [field]: value }));

  const clearFilters = () => {
    setSearch("");
    setAdvanced(DEFAULT_ADVANCED);
  };

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();

    return complaints
      .filter((c) => filter === "All" || c.status === filter)
      .filter((c) => {
        if (!q) return true;
        const caseNo = String(c.id).padStart(4, "0");
        return (
          c.location?.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q) ||
          c.reportedBy?.toLowerCase().includes(q) ||
          caseNo.includes(q) ||
          `#${caseNo}`.includes(q)
        );
      })
      .filter((c) => advanced.hazard === "All" || c.hazard === advanced.hazard)
      .filter((c) => !advanced.needsHelpOnly || c.needsHelp)
      .filter((c) => !advanced.dateFrom || c.createdAt >= advanced.dateFrom)
      .filter((c) => !advanced.dateTo || c.createdAt <= advanced.dateTo)
      .sort((a, b) =>
        advanced.sortBy === "oldest"
          ? a.createdAt.localeCompare(b.createdAt)
          : b.createdAt.localeCompare(a.createdAt)
      );
  }, [complaints, filter, search, advanced]);

  const handleAssign = (id) => {
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
    setAssigningId(id);
  };

  // #11/#12 — the modal collects crew, worker count, equipment and
  // vehicle together, so they land in a single updateComplaint call
  // (same "one merge, one source of truth" pattern as everything else
  // built on top of updateComplaint) alongside the status flip that
  // used to happen on its own.
  const handleAssignSubmit = async (allocation) => {
    const result = await updateComplaint(assigningId, {
      ...allocation,
      status: "In Progress",
    });
    if (result.success) {
      notify(`Crew assigned to case #${String(assigningId).padStart(4, "0")}`, "success");
      setAssigningId(null);
    } else {
      notify(result.error || "Couldn't assign crew.", "error");
    }
    return result;
  };

  const assigningComplaint = complaints.find((c) => c.id === assigningId);

  return (
    <div className="page">
      <h1>Supervisor Dashboard</h1>

      <div className="dashboard-toolbar">
        <div className="search-wrap">
          <IconSearch />
          <input
            type="text"
            className="search-input"
            placeholder="Search by location, description, case no. or reporter..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button
              type="button"
              className="search-clear-btn"
              onClick={() => setSearch("")}
              aria-label="Clear search"
            >
              <IconX />
            </button>
          )}
        </div>
        <button
          type="button"
          className={`filter-toggle-btn ${showAdvanced ? "active" : ""} ${advancedActive ? "has-value" : ""}`}
          onClick={() => setShowAdvanced((v) => !v)}
        >
          <IconSliders /> Advanced Filters
        </button>
      </div>

      {showAdvanced && (
        <div className="adv-filters-panel">
          <div className="adv-filters-grid">
            <label>
              Hazard Type
              <select
                value={advanced.hazard}
                onChange={(e) => handleAdvancedChange("hazard", e.target.value)}
              >
                <option value="All">All Hazards</option>
                {HAZARD_TYPES.map((h) => (
                  <option key={h} value={h}>
                    {h}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Sort By
              <select
                value={advanced.sortBy}
                onChange={(e) => handleAdvancedChange("sortBy", e.target.value)}
              >
                {SORT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Reported From
              <input
                type="date"
                value={advanced.dateFrom}
                onChange={(e) => handleAdvancedChange("dateFrom", e.target.value)}
              />
            </label>

            <label>
              Reported To
              <input
                type="date"
                value={advanced.dateTo}
                onChange={(e) => handleAdvancedChange("dateTo", e.target.value)}
              />
            </label>

            <label className="checkbox-field">
              <input
                type="checkbox"
                checked={advanced.needsHelpOnly}
                onChange={(e) => handleAdvancedChange("needsHelpOnly", e.target.checked)}
              />
              Support Requested Only
            </label>
          </div>

          {(advancedActive || search) && (
            <button type="button" className="clear-filters-btn" onClick={clearFilters}>
              <IconX /> Clear All Filters
            </button>
          )}
        </div>
      )}

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

      <p className="results-count">
        {filtered.length} {filtered.length === 1 ? "complaint" : "complaints"} found
      </p>

      {filtered.length === 0 ? (
        <p>No complaints match your search and filters.</p>
      ) : (
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
      )}

      {assigningComplaint && (
        <AssignCrewModal
          complaint={assigningComplaint}
          onClose={() => setAssigningId(null)}
          onSubmit={handleAssignSubmit}
        />
      )}
    </div>
  );
}