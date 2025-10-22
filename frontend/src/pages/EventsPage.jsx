// src/pages/EventsPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import EventFilters from "@/components/events/EventFilters";
import EventsList from "@/components/events/EventsList";
import { useEvents } from "@/hooks/useEvents";

export default function EventsPage() {
  const [filters, setFilters] = useState({});
  const { data: events = [], isLoading, isError, refetch } = useEvents(filters);

  return (
    <div className="p-6 space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent">
            Explore Events
          </h1>
          <p className="text-gray-500 mt-1">
            Discover and join conferences, meetups, and summits around the world.
          </p>
        </div>

        <Link to="/create-event">
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white shadow-md shadow-purple-300/30">
            <Plus className="w-4 h-4" />
            Create Event
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white/60 backdrop-blur-sm border border-gray-200 p-4 rounded-xl shadow-sm">
        <EventFilters onChange={setFilters} />
      </div>

      {/* Events List */}
      <div className="min-h-[250px]">
        {isLoading && (
          <div className="text-gray-500 animate-pulse text-center py-10">
            Loading events...
          </div>
        )}

        {isError && (
          <div className="text-center text-red-500 py-10">
            Failed to load events.
            <button
              onClick={refetch}
              className="ml-2 underline text-blue-600 hover:text-blue-700"
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !isError && events.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            No events found. Try adjusting your filters.
          </div>
        )}

        {!isLoading && !isError && events.length > 0 && (
          <EventsList events={events} />
        )}
      </div>
    </div>
  );
}
