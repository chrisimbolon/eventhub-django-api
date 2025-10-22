import React from "react";
import { Link } from "react-router-dom";
import Button from "../common/Button";
import CapacityBar from "../common/CapacityBar";

export default function EventCard({ event }) {
  const {
    id, title, start_date, end_date, capacity, attendees_count, venue, tags = []
  } = event;

  return (
    <article className="bg-white rounded-lg shadow p-4 flex flex-col">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="text-xs text-gray-500">{venue?.name || "Online"}</div>
      </div>

      <p className="text-sm text-gray-600 mt-2">
        {new Date(start_date).toLocaleDateString()} — {new Date(end_date).toLocaleDateString()}
      </p>

      <div className="mt-3">
        <CapacityBar value={attendees_count} max={capacity} />
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {tags.slice(0,3).map(t => <span key={t} className="text-xs px-2 py-1 bg-gray-100 rounded">{t}</span>)}
      </div>

      <div className="mt-4 flex items-center gap-2">
        <Link to={`/events/${id}`} className="flex-1">
          <Button className="w-full bg-blue-600 text-white hover:bg-blue-700">View</Button>
        </Link>
      </div>
    </article>
  );
}
