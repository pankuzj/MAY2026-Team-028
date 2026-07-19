import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconReport, IconClipboard, IconBroom, IconGrid } from "./Icons";

const roleLinks = {
  citizen: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/report", label: "Report", icon: IconReport },
    { to: "/my-complaints", label: "Mine", icon: IconClipboard },
  ],
  crew: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/crew", label: "Tasks", icon: IconBroom },
  ],
  admin: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/dashboard", label: "Admin", icon: IconGrid },
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
          <link.icon />
          <span className="label">{link.label}</span>
        </Link>
      ))}
    </nav>
  );
}
