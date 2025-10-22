// src/pages/EventsPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";  
import { Plus } from "lucide-react";      
import { Button } from "@/components/ui/button"; 
import EventFilters from "../components/events/EventFilters";
import EventsList from "../components/events/EventsList";
import { useEvents } from "../hooks/useEvents";

export default function EventsPage() {
  const [filters, setFilters] = useState({});
  const { data, isLoading } = useEvents(filters);

  return (
    <div className="space-y-6">

      <Link to="/create-event">
          <Button className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white">
            <Plus className="w-4 h-4" />
            Create Event
          </Button>
        </Link>

      <EventFilters onChange={setFilters} />
      <div>
        {isLoading ? <div>Loading...</div> : <EventsList events={data || []} />}
      </div>
    </div>
  );
}