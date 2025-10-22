import React from "react";
import Dashboard from "../dashboard/Dashboard";
import EventsTable from "./EventsTable";

export default function AdminDashboard({ metrics, events, onEdit, onDelete, onExport }) {
  return (
    <div className="space-y-6">
      <Dashboard metrics={metrics} />
      <div>
        <h2 className="text-lg font-semibold mb-3">Events</h2>
        <EventsTable events={events} onEdit={onEdit} onDelete={onDelete} onExport={onExport} />
      </div>
    </div>
  );
}
