import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

export const DEMO_USERS = [
  { username: "citizen", password: "citizen123", role: "citizen", name: "Sagnik Halder", label: "Citizen 1 (Sagnik)" },
  { username: "anita", password: "anita123", role: "citizen", name: "Anita Rao", label: "Citizen 2 (Anita)" },
  { username: "mohammed", password: "mohammed123", role: "citizen", name: "Mohammed Iqbal", label: "Citizen 3 (Mohammed)" },
  { username: "crew", password: "crew123", role: "crew", name: "Suresh Patil", label: "Cleanup Crew" },
  { username: "admin", password: "admin123", role: "admin", name: "Admin", label: "Ward Supervisor / Admin" },
];

const getStoredUser = () => {
  try {
    const raw = localStorage.getItem("smartsweep-user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);

  useEffect(() => {
    if (user) localStorage.setItem("smartsweep-user", JSON.stringify(user));
    else localStorage.removeItem("smartsweep-user");
  }, [user]);

  const login = (username, password) => {
    const match = DEMO_USERS.find(
      (u) => u.username === username.trim().toLowerCase() && u.password === password
    );
    if (!match) return { success: false, error: "Invalid username or password." };
    setUser({ username: match.username, role: match.role, name: match.name });
    return { success: true, role: match.role, name: match.name };
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);