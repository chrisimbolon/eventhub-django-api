// src/contexts/AuthProvider.jsx

import { getProfile, login as loginAPI, registerUser } from "@/api/auth";
import { createContext, useEffect, useState } from "react";

export const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      loadUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const normalizeUser = (rawUser) => {
    const fullName = `${rawUser.first_name || ""} ${rawUser.last_name || ""}`.trim();

    return {
      ...rawUser,
      name:
        fullName ||
        rawUser.username ||
        rawUser.email?.split("@")[0] ||
        "User",
    };
  };

  const loadUserProfile = async () => {
    try {
      const userData = await getProfile();
      setUser(normalizeUser(userData));
    } catch (error) {
      console.error("Failed to load user profile:", error);
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await loginAPI(credentials);
    localStorage.setItem("access_token", response.access);
    localStorage.setItem("refresh_token", response.refresh);
    await loadUserProfile();
    return response;
  };

  const register = async (userData) => {
    const registerData = {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      password_confirm: userData.password_confirm,
      first_name: userData.first_name,
      last_name: userData.last_name,
      role: userData.role || "attendee",
    };

    const response = await registerUser(registerData);
    await login({ username: userData.username, password: userData.password });
    return response;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === "admin",
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;
