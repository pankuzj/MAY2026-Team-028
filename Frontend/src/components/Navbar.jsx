import { Link, useLocation, useNavigate } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { IconReport, IconClipboard, IconBroom, IconGrid, IconLogOut, IconUsers, IconTruck, IconFeed, IconPackage } from "./Icons";

const roleLinks = {
  citizen: [
    { to: "/report", label: "Report Issue", icon: IconReport },
    { to: "/my-complaints", label: "My Complaints", icon: IconClipboard },
    { to: "/bulk-pickup", label: "Bulk Pickup", icon: IconPackage },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
  crew: [
    { to: "/crew", label: "Tasks", icon: IconBroom },
    { to: "/workforce", label: "Workforce", icon: IconUsers },
    { to: "/vehicles", label: "Vehicles", icon: IconTruck },
    { to: "/bulk-pickup-manage", label: "Bulk Pickups", icon: IconPackage },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
  admin: [
    { to: "/dashboard", label: "Dashboard", icon: IconGrid },
    { to: "/workforce", label: "Workforce & Tools", icon: IconUsers },
    { to: "/vehicles", label: "Fleet & Vehicles", icon: IconTruck },
    { to: "/bulk-pickup-manage", label: "Bulk Pickups", icon: IconPackage },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
};

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { notify } = useToast();
  const isActive = (path) => (location.pathname === path ? "active" : "");

  const handleLogout = () => {
    logout();
    notify("Logged out", "info");
    navigate("/login", { replace: true });
  };

  const links = user ? roleLinks[user.role] || [] : [];

  return (
    <nav className="navbar">
      <Link to={user ? "/" : "/login"} className="brand">
        <span className="brand-mark">
          <IconBroom />
        </span>
        SmartSweep
      </Link>
      {user && (
        <div className="nav-links desktop-nav-links">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className={isActive(l.to)}>
              <l.icon />
              {l.label}
            </Link>
          ))}
        </div>
      )}
      <div className="navbar-right">
        {user && (
          <>
            <span className="user-badge desktop-nav-links">{user.name}</span>
            <button className="logout-btn" onClick={handleLogout}>
              <IconLogOut />
              Log Out
            </button>
          </>
        )}
        <ThemeToggle />
      </div>
    </nav>
  );
}