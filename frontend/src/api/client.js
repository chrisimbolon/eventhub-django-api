// src/api/client.js

import axios from "axios";

const getBaseURL = () => {
  // If VITE_API_URL is set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Otherwise, check if we're in production (deployed)
  if (window.location.hostname === 'eventhub.chrisimbolon.dev') {
    return 'https://eventhub.chrisimbolon.dev/api/v1';
  }
  
  // Default to localhost for dev
  return 'http://localhost:8000/api/v1';
};


const api = axios.create({
  baseURL: getBaseURL(),
  headers: { 
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor 
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor 
// Response interceptor 
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) {
          window.location.href = "/auth";
          return Promise.reject(error);
        }

        const response = await api.post("/auth/refresh/", { refresh: refreshToken });

        const { access } = response.data;
        localStorage.setItem("access_token", access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/auth";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

