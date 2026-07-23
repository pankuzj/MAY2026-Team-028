import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconReport, IconClipboard, IconBroom, IconGrid, IconArrowRight, IconUsers, IconTruck, IconFeed, IconPackage } from "../components/Icons";

const roleConfig = {
  citizen: {
    heading: "Citizen Portal",
    blurb: "Report garbage issues, track status, and view community impact.",
    actions: [
      { to: "/report", label: "File a Report", icon: IconReport },
      { to: "/my-complaints", label: "My Complaints", icon: IconClipboard },
      { to: "/bulk-pickup", label: "Schedule Bulk Pickup", icon: IconPackage },
      { to: "/feed", label: "Public Transparency Feed", icon: IconFeed },
    ],
  },
  crew: {
    heading: "Cleanup Crew Portal",
    blurb: "View assigned tasks, update machinery status, and manage fleet vehicles.",
    actions: [
      { to: "/crew", label: "Assigned Tasks", icon: IconBroom },
      { to: "/workforce", label: "Workforce & Equipment", icon: IconUsers },
      { to: "/vehicles", label: "Vehicle Fleet", icon: IconTruck },
      { to: "/bulk-pickup-manage", label: "Bulk Pickup Management", icon: IconPackage },
      { to: "/feed", label: "Public Transparency Feed", icon: IconFeed },
    ],
  },
  admin: {
    heading: "Operations Console",
    blurb: "Manage complaints, allocate workforce & equipment, dispatch fleet, and oversee public feed.",
    actions: [
      { to: "/dashboard", label: "Open Dashboard", icon: IconGrid },
      { to: "/workforce", label: "Workforce & Equipment", icon: IconUsers },
      { to: "/vehicles", label: "Vehicle Assignment", icon: IconTruck },
      { to: "/bulk-pickup-manage", label: "Bulk Pickup Management", icon: IconPackage },
      { to: "/feed", label: "Public Feed Audit", icon: IconFeed },
    ],
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
            <span className="role-card-icon"><a.icon /></span>
            <h2>{a.label}</h2>
            <span className="card-arrow">Open <IconArrowRight /></span>
          </div>
        ))}
      </div>
    </div>
  );
}
