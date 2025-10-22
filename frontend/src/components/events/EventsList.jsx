import React from "react";
import EventCard from "./EventCard";

export default function EventsList({ events = [], loading = false }) {
  if (loading) return <div className="text-gray-500 animate-pulse">Loading events...</div>;
  if (!events.length) return <div className="text-gray-500">No events found.</div>;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {events.map((ev) => (
        <EventCard key={ev.id} event={ev} />
      ))}
    </div>
  );
}
