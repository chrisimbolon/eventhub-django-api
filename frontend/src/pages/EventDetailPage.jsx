// src/pages/EventDetailPage.jsx

import { useParams } from "react-router-dom";
import EventDetail from "../components/events/EventDetail";
import { useEvent } from "../hooks/useEvents";

export default function EventDetailPage() {
  const { slug } = useParams();
  const { data, isLoading } = useEvent(slug);

  if (isLoading) return <div>Loading...</div>;
  if (!data) return <div>Not Found</div>;

  return <EventDetail event={data} />;
}
