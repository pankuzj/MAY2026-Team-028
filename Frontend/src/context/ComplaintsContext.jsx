import { createContext, useContext, useState } from "react";

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
];

export function ComplaintsProvider({ children }) {
  const [complaints, setComplaints] = useState(initialComplaints);

  // All mutators are Promise-returning even though today they just touch
  // local state. That keeps every call site already using `await`, so
  // swapping the body for a `fetch()` to a FastAPI backend later won't
  // require touching any component.

  const addComplaint = (data) =>
    new Promise((resolve) => {
      setComplaints((prev) => {
        const newComplaint = {
          id: prev.length ? Math.max(...prev.map((c) => c.id)) + 1 : 1,
          status: "Pending",
          createdAt: new Date().toISOString().slice(0, 10),
          ...data,
        };
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
  const updateStatus = (id, status) => updateComplaint(id, { status });

  return (
    <ComplaintsContext.Provider
      value={{ complaints, addComplaint, updateStatus, updateComplaint, cancelComplaint }}
    >
      {children}
    </ComplaintsContext.Provider>
  );
}

export const useComplaints = () => useContext(ComplaintsContext);
