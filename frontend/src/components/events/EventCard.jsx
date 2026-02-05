// src/components/events/EventCard.jsx

import { Link } from "react-router-dom";
import Button from "../common/Button";
import CapacityBar from "../common/CapacityBar";

export default function EventCard({ event }) {
  if (!event) return null;

  const {
    id,
    title,
    start_date,
    end_date,
    city,
    country,
    venue_name,
    capacity,
    current_attendees,
    available_spots,
    is_registration_open,
    banner_image,
    organizer_name,
  } = event;

  const startDate = new Date(start_date).toLocaleDateString();
  const endDate = new Date(end_date).toLocaleDateString();

  return (
    <article className="bg-white rounded-lg shadow hover:shadow-md transition-all overflow-hidden flex flex-col">
      {banner_image && (
        <img
          src={banner_image}
          alt={title}
          className="w-full h-40 object-cover"
        />
      )}

      <div className="p-4 flex flex-col flex-grow">
        <h3 className="text-lg font-semibold text-gray-800 line-clamp-1">
          {title}
        </h3>
        <p className="text-xs text-gray-500 mt-1">
          Organized by {organizer_name}
        </p>

        <p className="text-sm text-gray-600 mt-2">
          {startDate} — {endDate}
        </p>
        <p className="text-sm text-gray-500">
          {venue_name || "Online"} • {city}, {country}
        </p>

        <div className="mt-3">
          <CapacityBar value={current_attendees} max={capacity} />
          <p className="text-xs text-gray-500 mt-1">
            {available_spots} spots left
          </p>
        </div>

        <div className="mt-4 flex items-center gap-2">
          {/* <Link to={`/events/${id}`} className="flex-1"> */}
          <Link to={`/events/${event.slug}`} className="flex-1">

            <Button className="w-full bg-blue-600 text-white hover:bg-blue-700">
              View Details
            </Button>
          </Link>

          {is_registration_open ? (
            <span className="text-xs text-green-600">Open</span>
          ) : (
            <span className="text-xs text-red-600">Closed</span>
          )}
        </div>
      </div>
    </article>
  );
}
