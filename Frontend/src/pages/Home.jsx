import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roleConfig = {
  citizen: {
    heading: "Citizen Portal",
    blurb: "Report garbage issues and track their status.",
    actions: [
      { to: "/report", label: "File a Report" },
      { to: "/my-complaints", label: "My Complaints" },
    ],
  },
  crew: {
    heading: "Cleanup Crew",
    blurb: "View assigned tasks and mark work complete.",
    actions: [{ to: "/crew", label: "Assigned Tasks" }],
  },
  admin: {
    heading: "Operations Console",
    blurb: "Manage incoming complaints and assign crews.",
    actions: [{ to: "/dashboard", label: "Open Dashboard" }],
  },
};

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const config = roleConfig[user.role];

  return (
    <div className="role-select">
      <span className="eyebrow">Welcome back, {user.name}</span>
      <h1>{config.heading}</h1>
      <p>{config.blurb}</p>
      <div className="role-cards">
        {config.actions.map((a) => (
          <div key={a.to} className="role-card" onClick={() => navigate(a.to)}>
            <h2>{a.label}</h2>
          </div>
        ))}
      </div>
    </div>
  );
}