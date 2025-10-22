import React from "react";
import Button from "../common/Button";
import CapacityBar from "../common/CapacityBar";

export default function EventDetail({ event, onRegister }) {
  if (!event) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="rounded-lg overflow-hidden shadow">
        <img src={event.banner_url} alt={event.title} className="w-full h-64 object-cover"/>
        <div className="p-4">
          <h1 className="text-2xl font-bold">{event.title}</h1>
          <p className="text-sm text-gray-600">{event.venue?.name || "Online"}</p>
          <p className="mt-3 text-gray-700">{event.description}</p>
          <div className="mt-4 flex items-center gap-4">
            <CapacityBar value={event.attendees_count} max={event.capacity} />
            <Button onClick={() => onRegister(event.id)} className="bg-blue-600 text-white">Register</Button>
          </div>
        </div>
      </div>

      <section>
        <h2 className="text-lg font-semibold">Sessions</h2>
        <div className="mt-3 space-y-2">
          {event.sessions?.map(s => (
            <div key={s.id} className="p-3 border rounded">
              <div className="flex justify-between">
                <div>
                  <div className="font-medium">{s.title}</div>
                  <div className="text-xs text-gray-500">{new Date(s.start_time).toLocaleString()} — {new Date(s.end_time).toLocaleTimeString()}</div>
                </div>
                <div className="text-sm text-gray-600">{s.track?.name}</div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
