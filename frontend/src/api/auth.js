// // src/api/auth.js
// import api from "./client";


// export const registerUser = async (data) => {
//   console.log("register payload →", data);
//   const res = await api.post("/auth/register/", data);
//   return res.data;
// };


// export const login = (credentials) =>
//   api.post("/auth/login/", credentials).then((res) => res.data);

// export const getProfile = () =>
//   api.get("/auth/profile/").then((res) => res.data);

// export const refreshToken = () =>
//   api.post("/auth/refresh/", {
//     refresh: localStorage.getItem("refresh_token"),
//   });


import api from "./client";

export const registerUser = async (data) => {
  try {
    const response = await api.post("/auth/register/", data);
    return response.data;
  } catch (error) {
    console.error("Registration API error:", error.response?.data);
    throw error;
  }
};

export const login = async (credentials) => {
  try {
    const response = await api.post("/auth/login/", credentials);
    return response.data;
  } catch (error) {
    console.error("Login API error:", error.response?.data);
    throw error;
  }
};

export const getProfile = async () => {
  try {
    const response = await api.get("/auth/profile/");
    return response.data;
  } catch (error) {
    console.error("Profile API error:", error.response?.data);
    throw error;
  }
};

export const updateProfile = async (data) => {
  try {
    const response = await api.patch("/auth/profile/", data);
    return response.data;
  } catch (error) {
    console.error("Update profile API error:", error.response?.data);
    throw error;
  }
};

export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem("refresh_token");
    const response = await api.post("/auth/refresh/", { refresh });
    return response.data;
  } catch (error) {
    console.error("Token refresh error:", error.response?.data);
    throw error;
  }
};
