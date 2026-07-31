import { createContext, useContext, useState } from "react";
import { useAuth } from "./AuthContext";
import { createComplaintApi } from "../utils/api";

const ComplaintsContext = createContext(null);

const initialComplaints = [
  {
    id: 1,
    location: "MG Road, Near Bus Stop",
    description: "Garbage overflowing for 3 days, foul smell.",
    hazard: "Foul Smell",
    photo: null,
    coords: { lat: 12.9716, lng: 77.5946 },
    reportedBy: "Anita Rao",
    status: "Pending",
    createdAt: "2026-06-20",
  },
  {
    id: 2,
    location: "5th Cross, Indiranagar",
    description: "Illegal dumping near park entrance.",
    hazard: "Mosquito Breeding",
    photo: null,
    coords: { lat: 12.9784, lng: 77.6408 },
    reportedBy: "Mohammed Iqbal",
    status: "In Progress",
    createdAt: "2026-06-18",
  },
  // The rest below only exist to give the Reports & Trends dashboard (#16)
  // something real to aggregate — a spread of statuses, hazard types and
  // dates instead of just the two rows above.
  {
    id: 3,
    location: "80 Feet Road, Koramangala",
    description: "Overflowing community bin attracting stray animals.",
    hazard: "Overflowing Bin",
    photo: null,
    coords: { lat: 12.9352, lng: 77.6146 },
    reportedBy: "Sagnik Halder",
    status: "Resolved",
    createdAt: "2026-06-10",
    resolvedAt: "2026-06-13",
  },
  {
    id: 4,
    location: "Jayanagar 4th Block Park",
    description: "Leaves and general litter piled near the entrance gate.",
    hazard: "None",
    photo: null,
    coords: { lat: 12.9254, lng: 77.5931 },
    reportedBy: "Anita Rao",
    status: "Resolved",
    createdAt: "2026-06-05",
    resolvedAt: "2026-06-06",
  },
  {
    id: 5,
    location: "MG Road Metro Station Exit",
    description: "Medical waste dumped near the footpath, children play nearby.",
    hazard: "Risk to Children",
    photo: null,
    coords: { lat: 12.9758, lng: 77.6069 },
    reportedBy: "Mohammed Iqbal",
    status: "Resolved",
    createdAt: "2026-06-15",
    resolvedAt: "2026-06-21",
  },
  {
    id: 6,
    location: "12th Main, Indiranagar",
    description: "Reported by mistake, bin was already cleared by the time I checked.",
    hazard: "None",
    photo: null,
    coords: { lat: 12.9719, lng: 77.6412 },
    reportedBy: "Sagnik Halder",
    status: "Cancelled",
    createdAt: "2026-06-22",
  },
  {
    id: 7,
    location: "Sony World Signal, Koramangala",
    description: "Foul smell from an uncollected bin for over a week.",
    hazard: "Foul Smell",
    photo: null,
    coords: { lat: 12.9343, lng: 77.6224 },
    reportedBy: "Anita Rao",
    status: "Pending",
    createdAt: "2026-07-01",
  },
  {
    id: 8,
    location: "Jayanagar 9th Block Market",
    description: "Vegetable market waste overflowing onto the road.",
    hazard: "Overflowing Bin",
    photo: null,
    coords: { lat: 12.9184, lng: 77.5847 },
    reportedBy: "Mohammed Iqbal",
    status: "In Progress",
    createdAt: "2026-06-28",
  },
];

export function ComplaintsProvider({ children }) {
  const [complaints, setComplaints] = useState(initialComplaints);
  const { user } = useAuth();

  // All mutators are Promise-returning even though today they just touch
  // local state. That keeps every call site already using `await`, so
  // swapping the body for a `fetch()` to a FastAPI backend later won't
  // require touching any component.

  const toLocalComplaint = (apiComplaint, fallbackData) => ({
    id: apiComplaint.id,
    location: apiComplaint.title || apiComplaint.address || fallbackData.location,
    description: apiComplaint.description || fallbackData.description,
    hazard: apiComplaint.category || fallbackData.hazard || "None",
    photo: apiComplaint.photo_url || fallbackData.photo || null,
    coords:
      apiComplaint.latitude != null && apiComplaint.longitude != null
        ? { lat: apiComplaint.latitude, lng: apiComplaint.longitude }
        : fallbackData.coords || null,
    reportedBy: user?.name || fallbackData.reportedBy || "Citizen",
    status:
      apiComplaint.status?.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase()) ||
      "Pending",
    createdAt: (apiComplaint.created_at || new Date().toISOString()).slice(0, 10),
    resolvedAt: apiComplaint.resolved_at ? apiComplaint.resolved_at.slice(0, 10) : undefined,
    cancelledAt: apiComplaint.cancelled_at ? apiComplaint.cancelled_at.slice(0, 10) : undefined,
  });

  const addComplaint = (data) =>
    new Promise(async (resolve) => {
      const result = await createComplaintApi({
        location: data.location,
        description: data.description,
        hazard: data.hazard,
        photo: data.photo,
        coords: data.coords,
        ward_id: user?.ward_id ?? null,
      });

      if (!result.success) {
        resolve({ success: false, error: result.error });
        return;
      }

      setComplaints((prev) => {
        const newComplaint = toLocalComplaint(result.data, data);
        resolve({ success: true, complaint: newComplaint });
        return [newComplaint, ...prev];
      });
    });

  // Generic partial update — merges `updates` into the matching complaint.
  // Every other mutator (status changes, feedback, assignment, hazard
  // flags, edits, etc.) should be built on top of this one function.
  const updateComplaint = (id, updates) =>
    new Promise((resolve) => {
      setComplaints((prev) => {
        const exists = prev.some((c) => c.id === id);
        if (!exists) {
          resolve({ success: false, error: "Complaint not found." });
          return prev;
        }
        resolve({ success: true });
        return prev.map((c) => (c.id === id ? { ...c, ...updates } : c));
      });
    });

  // A citizen may only withdraw a complaint while it's still Pending —
  // once a crew is assigned or it's resolved, cancelling stops making sense.
  const cancelComplaint = (id) =>
    new Promise((resolve) => {
      setComplaints((prev) => {
        const target = prev.find((c) => c.id === id);
        if (!target) {
          resolve({ success: false, error: "Complaint not found." });
          return prev;
        }
        if (target.status !== "Pending") {
          resolve({
            success: false,
            error: "Only pending complaints can be withdrawn.",
          });
          return prev;
        }
        resolve({ success: true });
        return prev.map((c) => (c.id === id ? { ...c, status: "Cancelled" } : c));
      });
    });

  // Kept for existing call sites (assign / mark complete); now a thin
  // wrapper around updateComplaint so there's one source of truth.
  // Stamps resolvedAt alongside the status flip to "Resolved" so the
  // Reports & Trends dashboard (#16) can compute resolution time without
  // every call site having to remember to pass it explicitly.
  const updateStatus = (id, status) =>
    updateComplaint(id, {
      status,
      ...(status === "Resolved" ? { resolvedAt: new Date().toISOString().slice(0, 10) } : {}),
    });

  return (
    <ComplaintsContext.Provider
      value={{ complaints, addComplaint, updateStatus, updateComplaint, cancelComplaint }}
    >
      {children}
    </ComplaintsContext.Provider>
  );
}

export const useComplaints = () => useContext(ComplaintsContext);
