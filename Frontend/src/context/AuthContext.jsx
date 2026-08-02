import { createContext, useContext, useEffect, useState } from "react";
import {
  clearStoredTokenPair,
  getMeApi,
  getStoredTokenPair,
  loginApi,
  registerApi,
} from "../utils/api";

const AuthContext = createContext(null);

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
  const [loading, setLoading] = useState(true);

  // Validate stored JWT token on mount
  useEffect(() => {
    async function restoreSession() {
      const { access } = getStoredTokenPair();
      if (access) {
        const result = await getMeApi();
        if (result.success && result.data) {
          const u = result.data;
          const userObj = {
            id: u.id,
            email: u.email,
            username: u.email.split("@")[0],
            name: u.full_name,
            role: u.role,
            ward_id: u.ward_id,
          };
          setUser(userObj);
          localStorage.setItem("smartsweep-user", JSON.stringify(userObj));
        } else {
          clearStoredTokenPair();
          setUser(null);
          localStorage.removeItem("smartsweep-user");
        }
      }
      setLoading(false);
    }
    restoreSession();
  }, []);

  useEffect(() => {
    if (user) {
      localStorage.setItem("smartsweep-user", JSON.stringify(user));
    } else {
      localStorage.removeItem("smartsweep-user");
    }
  }, [user]);

  const login = async (username, password) => {
    const loginRes = await loginApi(username, password);

    if (!loginRes.success) {
      return { success: false, error: loginRes.error };
    }

    const meRes = await getMeApi();
    if (!meRes.success || !meRes.data) {
      return { success: false, error: "Failed to fetch user profile." };
    }

    const profile = meRes.data;
    const userObj = {
      id: profile.id,
      email: profile.email,
      username: profile.email.split("@")[0],
      name: profile.full_name,
      role: profile.role,
      ward_id: profile.ward_id,
    };

    setUser(userObj);
    return { success: true, role: profile.role, name: profile.full_name };
  };

  const register = async (userData) => {
    const result = await registerApi(userData);
    if (!result.success) {
      return { success: false, error: result.error };
    }
    return { success: true, user: result.data };
  };

  const logout = () => {
    clearStoredTokenPair();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
