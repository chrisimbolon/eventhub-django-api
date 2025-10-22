// src/pages/Home.jsx

import React from "react";
import HeroSection from "../components/dashboard/HeroSection";
import EventsList from "../components/events/EventsList";
import { useEvents } from "../hooks/useEvents";

export default function Home() {
  const { data, isLoading } = useEvents({});

  return (
    <div className="space-y-6">
      <HeroSection title="Eventhub" subtitle="Find the events that don't hug the crowd" />
      <section>
        <h2 className="text-xl font-semibold mb-3">Upcoming events</h2>
        {isLoading ? <div>Loading...</div> : <EventsList events={data || []} />}
      </section>
    </div>
  );
}
