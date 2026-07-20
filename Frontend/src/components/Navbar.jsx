import { Link, useLocation, useNavigate } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { IconReport, IconClipboard, IconBroom, IconGrid, IconLogOut, IconUsers, IconFeed } from "./Icons";

const roleLinks = {
  citizen: [
    { to: "/report", label: "Report Issue", icon: IconReport },
    { to: "/my-complaints", label: "My Complaints", icon: IconClipboard },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
  crew: [
    { to: "/crew", label: "Tasks", icon: IconBroom },
    { to: "/workforce", label: "Workforce", icon: IconUsers },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
  admin: [
    { to: "/dashboard", label: "Dashboard", icon: IconGrid },
    { to: "/workforce", label: "Workforce & Tools", icon: IconUsers },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
};

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { notify } = useToast();

  const links = user ? roleLinks[user.role] || [] : [];

  const handleLogout = () => {
    logout();
    notify("Logged out successfully.", "info");
    navigate("/");
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="brand">
          <span className="brand-dot" />
          <span className="brand-text">Smart<span className="brand-accent">Sweep</span></span>
        </Link>

        {user && (
          <nav className="nav-links">
            {links.map((link) => {
              const Icon = link.icon;
              const active = location.pathname === link.to;
              return (
                <Link key={link.to} to={link.to} className={`nav-item ${active ? "active" : ""}`}>
                  <Icon />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        )}

        <div className="nav-right">
          <ThemeToggle />
          {user && (
            <div className="user-badge">
              <span className="role-pill">{user.role}</span>
              <span className="user-name">{user.name}</span>
              <button className="logout-btn" onClick={handleLogout} title="Log out">
                <IconLogOut />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
