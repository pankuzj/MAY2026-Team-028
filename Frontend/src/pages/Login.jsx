import { useState } from "react";
import { Navigate, useNavigate, useLocation } from "react-router-dom";
import { useAuth, DEMO_USERS } from "../context/AuthContext";

const roleHome = { citizen: "/report", crew: "/crew", admin: "/dashboard" };

export default function Login() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [activeRole, setActiveRole] = useState("citizen");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (user) return <Navigate to={roleHome[user.role] || "/"} replace />;

  const fillDemo = (demoUser) => {
    setActiveRole(demoUser.role);
    setUsername(demoUser.username);
    setPassword(demoUser.password);
    setError("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const result = login(username, password);
    if (!result.success) {
      setError(result.error);
      return;
    }
    navigate(location.state?.from || roleHome[result.role] || "/", { replace: true });
  };

  return (
    <div className="login-page">
      <span className="eyebrow">Restricted Access</span>
      <h1>SmartSweep</h1>
      <p className="login-sub">Sign in to continue</p>

      <div className="role-tabs">
        {DEMO_USERS.map((u) => (
          <button
            key={u.role}
            type="button"
            className={activeRole === u.role ? "active" : ""}
            onClick={() => fillDemo(u)}
          >
            {u.label}
          </button>
        ))}
      </div>

      <form className="login-form" onSubmit={handleSubmit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" required />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" required />
        </label>
        {error && <p className="loc-error">{error}</p>}
        <button type="submit">Access System</button>
      </form>

      <div className="demo-hint">
        <span className="eyebrow">Demo Credentials</span>
        {DEMO_USERS.map((u) => (
          <p key={u.role}><strong>{u.label}:</strong> {u.username} / {u.password}</p>
        ))}
      </div>
    </div>
  );
}