import React from "react";
import AdminDashboard from "../components/admin/AdminDashboard";
import { useAdminMetrics, useEvents as useEventsQuery } from "../hooks/useEvents";

export default function AdminPage() {
  const { data: metrics } = useAdminMetrics();
  const { data: events } = useEventsQuery({});

  const handleEdit = (ev) => { console.log("edit", ev); };
  const handleDelete = (id) => { console.log("delete", id); };
  const handleExport = (id) => { console.log("export", id); };

  return <AdminDashboard metrics={metrics || {}} events={events || []} onEdit={handleEdit} onDelete={handleDelete} onExport={handleExport} />;
}
