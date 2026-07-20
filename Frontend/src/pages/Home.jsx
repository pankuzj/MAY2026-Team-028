import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconReport, IconClipboard, IconBroom, IconGrid, IconArrowRight, IconUsers, IconFeed } from "../components/Icons";

const roleConfig = {
  citizen: {
    heading: "Citizen Portal",
    blurb: "Report garbage issues, track status, and view community impact.",
    actions: [
      { to: "/report", label: "File a Report", icon: IconReport },
      { to: "/my-complaints", label: "My Complaints", icon: IconClipboard },
      { to: "/feed", label: "Public Transparency Feed", icon: IconFeed },
    ],
  },
  crew: {
    heading: "Cleanup Crew Portal",
    blurb: "View assigned tasks, update machinery status, and manage fleet vehicles.",
    actions: [
      { to: "/crew", label: "Assigned Tasks", icon: IconBroom },
      { to: "/workforce", label: "Workforce & Equipment", icon: IconUsers },
      { to: "/feed", label: "Public Transparency Feed", icon: IconFeed },
    ],
  },
  admin: {
    heading: "Operations Console",
    blurb: "Manage complaints, allocate workforce & equipment, dispatch fleet, and oversee public feed.",
    actions: [
      { to: "/dashboard", label: "Open Dashboard", icon: IconGrid },
      { to: "/workforce", label: "Workforce & Equipment", icon: IconUsers },
      { to: "/feed", label: "Public Feed Audit", icon: IconFeed },
    ],
  },
};

export default function Home() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <div className="page page-center">
        <div className="hero-card">
          <span className="eyebrow">Smart City Sanitation Management</span>
          <h1>Smart<span className="brand-accent">Sweep</span> Portal</h1>
          <p className="hero-lead">
            Select your role to access garbage reporting, crew dispatches, and supervisor insights.
          </p>
          <div className="role-selector">
            <button className="role-btn citizen" onClick={() => login("citizen")}>
              <IconReport />
              <div>
                <strong>Continue as Citizen</strong>
                <small>Report issues & track status</small>
              </div>
            </button>
            <button className="role-btn crew" onClick={() => login("crew")}>
              <IconBroom />
              <div>
                <strong>Continue as Crew</strong>
                <small>View & resolve assigned tasks</small>
              </div>
            </button>
            <button className="role-btn admin" onClick={() => login("admin")}>
              <IconGrid />
              <div>
                <strong>Continue as Supervisor</strong>
                <small>Overview & team dispatch</small>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const config = roleConfig[user.role] || roleConfig.citizen;

  return (
    <div className="page">
      <div className="dashboard-welcome">
        <div>
          <span className="eyebrow">Welcome back</span>
          <h1>{user.name}</h1>
          <p className="lead">{config.blurb}</p>
        </div>
        <span className="role-badge-lg">{user.role}</span>
      </div>

      <div className="home-actions-grid">
        {config.actions.map((act) => {
          const Icon = act.icon;
          return (
            <button key={act.to} className="action-card" onClick={() => navigate(act.to)}>
              <div className="action-card-header">
                <Icon />
                <IconArrowRight className="arrow-icon" />
              </div>
              <div className="action-card-body">
                <h3>{act.label}</h3>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
