// src/pages/EventDetailPage.jsx


import React from "react";
import { useParams } from "react-router-dom";
import { useEvent } from "../hooks/useEvents";
import EventDetail from "../components/events/EventDetail";

export default function EventDetailPage() {
  const { id } = useParams();
  const { data, isLoading } = useEvent(id);

  if (isLoading) return <div>Loading...</div>;
  if (!data) return <div>Not Found</div>;

  return <EventDetail event={data} />;
}
