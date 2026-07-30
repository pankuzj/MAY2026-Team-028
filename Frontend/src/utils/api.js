/**
 * API Client helper module for communicating with the SmartSweep FastAPI backend.
 * Handles JWT authentication headers, token storage, auto-refresh, and error envelopes.
 */

const API_BASE_URL = "/api/v1";

export const getStoredTokenPair = () => {
  try {
    const access = localStorage.getItem("smartsweep-access-token");
    const refresh = localStorage.getItem("smartsweep-refresh-token");
    return { access, refresh };
  } catch {
    return { access: null, refresh: null };
  }
};

export const setStoredTokenPair = (accessToken, refreshToken) => {
  if (accessToken) localStorage.setItem("smartsweep-access-token", accessToken);
  else localStorage.removeItem("smartsweep-access-token");

  if (refreshToken) localStorage.setItem("smartsweep-refresh-token", refreshToken);
  else localStorage.removeItem("smartsweep-refresh-token");
};

export const clearStoredTokenPair = () => {
  localStorage.removeItem("smartsweep-access-token");
  localStorage.removeItem("smartsweep-refresh-token");
};

export async function apiFetch(endpoint, options = {}) {
  const { access } = getStoredTokenPair();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (access) {
    headers["Authorization"] = `Bearer ${access}`;
  }

  const config = {
    ...options,
    headers,
  };

  let response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  // Auto-refresh token on 401 UNAUTHENTICATED
  if (response.status === 401 && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/refresh")) {
    const { refresh } = getStoredTokenPair();
    if (refresh) {
      const refreshed = await refreshTokenApi(refresh);
      if (refreshed.success) {
        headers["Authorization"] = `Bearer ${refreshed.access_token}`;
        response = await fetch(`${API_BASE_URL}${endpoint}`, { ...config, headers });
      } else {
        clearStoredTokenPair();
      }
    }
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data?.error?.message || data?.message || "An unexpected error occurred.";
    const errorCode = data?.error?.code || "API_ERROR";
    return { success: false, status: response.status, error: errorMsg, code: errorCode, details: data?.error?.details };
  }

  return { success: true, data };
}

// Authentication API calls
export async function loginApi(email, password) {
  const result = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  if (result.success) {
    setStoredTokenPair(result.data.access_token, result.data.refresh_token);
  }

  return result;
}

export async function registerApi(userData) {
  const result = await apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });

  return result;
}

export async function getMeApi() {
  return await apiFetch("/auth/me");
}

export async function refreshTokenApi(refreshToken) {
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  const data = await response.json().catch(() => ({}));
  if (response.ok && data.access_token) {
    setStoredTokenPair(data.access_token, data.refresh_token);
    return { success: true, access_token: data.access_token, refresh_token: data.refresh_token };
  }

  return { success: false };
}
