import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { IconHome, IconReport, IconClipboard, IconBroom, IconGrid, IconUsers, IconTruck, IconFeed, IconPackage } from "./Icons";

const roleLinks = {
  citizen: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/report", label: "Report", icon: IconReport },
    { to: "/my-complaints", label: "Mine", icon: IconClipboard },
    { to: "/bulk-pickup", label: "Bulk", icon: IconPackage },
    { to: "/feed", label: "Feed", icon: IconFeed },
  ],
  crew: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/crew", label: "Tasks", icon: IconBroom },
    { to: "/workforce", label: "Crew", icon: IconUsers },
    { to: "/vehicles", label: "Fleet", icon: IconTruck },
    { to: "/bulk-pickup-manage", label: "Bulk", icon: IconPackage },
    { to: "/feed", label: "Feed", icon: IconFeed },
  ],
  admin: [
    { to: "/", label: "Home", icon: IconHome },
    { to: "/dashboard", label: "Admin", icon: IconGrid },
    { to: "/workforce", label: "Crew", icon: IconUsers },
    { to: "/vehicles", label: "Fleet", icon: IconTruck },
    { to: "/bulk-pickup-manage", label: "Bulk", icon: IconPackage },
    { to: "/feed", label: "Feed", icon: IconFeed },
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
