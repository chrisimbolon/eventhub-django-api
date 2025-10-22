// src/api/events.js

import api from "./client";

// Fetch all events
export const fetchEvents = (params) =>
  api.get("/events/", { params }).then((r) => r.data);

// Fetch single event by slug (not ID)
export const fetchEvent = (slug) =>
  api.get(`/events/${slug}/`).then((r) => r.data);

// Register attendee
export const registerAttendee = (eventSlug, payload) =>
  api.post(`/events/${eventSlug}/register/`, payload).then((r) => r.data);

// Admin endpoints
export const fetchAdminMetrics = () =>
  api.get("/admin/metrics/").then((r) => r.data);

export const fetchSessions = (eventSlug) =>
  api.get(`/events/${eventSlug}/sessions/`).then((r) => r.data);

export const createSession = (eventSlug, payload) =>
  api.post(`/events/${eventSlug}/sessions/`, payload).then((r) => r.data);

export const exportAttendeesCsv = (eventSlug) =>
  api
    .get(`/events/${eventSlug}/export/`, { responseType: "blob" })
    .then((r) => r.data);

// ✅ Create new event
export const createEvent = async (data) => {
  try {
    const response = await api.post("/events/", data);
    return response.data;
  } catch (error) {
    console.error("Error creating event:", error.response?.data || error);
    throw error;
  }
};
