// src/hooks/useEvents.js
// src/hooks/useEvents.js
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchEvents,
  fetchEvent,
  registerAttendee,
  fetchAdminMetrics,
} from "../api/events";

// ✅ List of events (with optional filters)
export const useEvents = (filters) => {
  return useQuery({
    queryKey: ["events", filters],
    queryFn: () => fetchEvents(filters),
    select: (data) => {
      // Transform paginated responses into flat arrays
      if (Array.isArray(data)) return data;
      return data?.results || [];
    },
    placeholderData: (prev) => prev,
  });
};

// ✅ Single event by ID
export const useEvent = (id) =>
  useQuery({
    queryKey: ["event", id],
    queryFn: () => fetchEvent(id),
    enabled: !!id,
  });

// ✅ Register attendee mutation
export const useRegister = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: ({ eventId, payload }) => registerAttendee(eventId, payload),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["event", variables.eventId] });
      qc.invalidateQueries({ queryKey: ["events"] });
    },
  });
};

// ✅ Admin metrics (dashboard stats)
export const useAdminMetrics = () =>
  useQuery({
    queryKey: ["admin-metrics"],
    queryFn: fetchAdminMetrics,
  });
