import { Link, useLocation, useNavigate } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { useAuth } from "../context/AuthContext";

const roleLinks = {
  citizen: [
    { to: "/report", label: "Report Issue" },
    { to: "/my-complaints", label: "My Complaints" },
  ],
  crew: [{ to: "/crew", label: "Assigned Tasks" }],
  admin: [{ to: "/dashboard", label: "Dashboard" }],
};

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const isActive = (path) => (location.pathname === path ? "active" : "");

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const links = user ? roleLinks[user.role] || [] : [];

  return (
    <nav className="navbar">
      <Link to={user ? "/" : "/login"} className="brand">SmartSweep</Link>
      {user && (
        <div className="nav-links desktop-nav-links">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className={isActive(l.to)}>{l.label}</Link>
          ))}
        </div>
      )}
      <div className="navbar-right">
        {user && (
          <>
            <span className="user-badge desktop-nav-links">{user.name}</span>
            <button className="logout-btn" onClick={handleLogout}>Log Out</button>
          </>
        )}
        <ThemeToggle />
      </div>
    </nav>
  );
}