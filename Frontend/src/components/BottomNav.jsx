import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconReport, IconClipboard, IconBroom, IconGrid, IconUsers, IconFeed } from "./Icons";

const roleLinks = {
  citizen: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/report", label: "Report", icon: IconReport },
    { to: "/my-complaints", label: "Mine", icon: IconClipboard },
    { to: "/feed", label: "Public Feed", icon: IconFeed },
  ],
  crew: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/crew", label: "Tasks", icon: IconBroom },
    { to: "/workforce", label: "Workforce", icon: IconUsers },
    { to: "/feed", label: "Feed", icon: IconFeed },
  ],
  admin: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/dashboard", label: "Admin", icon: IconGrid },
    { to: "/workforce", label: "Workforce", icon: IconUsers },
    { to: "/feed", label: "Feed", icon: IconFeed },
  ],
};

export default function BottomNav() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) return null;
  const links = roleLinks[user.role] || [];

  return (
    <nav className="bottom-nav">
      {links.map((link) => {
        const Icon = link.icon;
        const active = location.pathname === link.to;
        return (
          <Link key={link.to} to={link.to} className={`bottom-nav-item ${active ? "active" : ""}`}>
            <Icon />
            <span>{link.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
