// src/api/auth.js

import api from "./client";

export const registerUser = async (data) => {
  try {
    // const response = await api.post("/auth/register/", data);
    const response = await api.post("/api/v1/auth/register/", data);

    return response.data;
  } catch (error) {
    console.error("Registration API error:", error.response?.data);
    throw error;
  }
};

export const login = async (credentials) => {
  try {
    const response = await api.post("/api/v1/auth/login/", credentials);
    // const response = await api.post("/auth/login/", credentials);
    return response.data;
  } catch (error) {
    console.error("Login API error:", error.response?.data);
    throw error;
  }
};

export const getProfile = async () => {
  try {
    const response = await api.get("/api/v1/auth/profile/");
    // const response = await api.get("/auth/profile/");
    return response.data;
  } catch (error) {
    console.error("Profile API error:", error.response?.data);
    throw error;
  }
};

export const updateProfile = async (data) => {
  try {
    const response = await api.patch("/api/v1/auth/profile/", data);
    // const response = await api.patch("/auth/profile/", data);
    return response.data;
  } catch (error) {
    console.error("Update profile API error:", error.response?.data);
    throw error;
  }
};

export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem("refresh_token");
    const response = await api.post("/api/v1/auth/refresh/", { refresh });
    // const response = await api.post("/auth/refresh/", { refresh });
    return response.data;
  } catch (error) {
    console.error("Token refresh error:", error.response?.data);
    throw error;
  }
};
