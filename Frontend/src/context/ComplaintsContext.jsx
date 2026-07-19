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

  const addComplaint = (data) => {
    setComplaints((prev) => [
      {
        id: prev.length ? Math.max(...prev.map((c) => c.id)) + 1 : 1,
        status: "Pending",
        createdAt: new Date().toISOString().slice(0, 10),
        ...data,
      },
      ...prev,
    ]);
  };

  const updateStatus = (id, status) => {
    setComplaints((prev) =>
      prev.map((c) => (c.id === id ? { ...c, status } : c))
    );
  };

  return (
    <ComplaintsContext.Provider value={{ complaints, addComplaint, updateStatus }}>
      {children}
    </ComplaintsContext.Provider>
  );
}

export const useComplaints = () => useContext(ComplaintsContext);
