import React from "react";
import HeroSection from "./HeroSection";
import StatCard from "./StatCard";

export default function Dashboard({ metrics = {} }) {
  return (
    <div className="space-y-6">
      <HeroSection title="Admin Dashboard" subtitle="Metrics & insights" />
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard title="Total events" value={metrics.total_events ?? "—"} />
        <StatCard title="Total attendees" value={metrics.total_attendees ?? "—"} />
        <StatCard title="Capacity used" value={metrics.capacity_used ?? "—"} />
      </div>
    </div>
  );
}
