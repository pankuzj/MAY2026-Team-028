import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roleLinks = {
  citizen: [
    { to: "/", label: "Home", icon: "🏠" },
    { to: "/report", label: "Report", icon: "📝" },
    { to: "/my-complaints", label: "Mine", icon: "📋" },
  ],
  crew: [
    { to: "/", label: "Home", icon: "🏠" },
    { to: "/crew", label: "Tasks", icon: "🧹" },
  ],
  admin: [
    { to: "/", label: "Home", icon: "🏠" },
    { to: "/dashboard", label: "Admin", icon: "🗂️" },
  ],
};

export default function BottomNav() {
  const location = useLocation();
  const { user } = useAuth();
  if (!user) return null;
  const links = roleLinks[user.role] || [];

  return (
    <nav className="bottom-nav">
      {links.map((link) => (
        <Link key={link.to} to={link.to} className={location.pathname === link.to ? "active" : ""}>
          <span className="icon">{link.icon}</span>
          <span className="label">{link.label}</span>
        </Link>
      ))}
    </nav>
  );
}