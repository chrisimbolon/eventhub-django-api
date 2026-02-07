// src/pages/EventDetailPage.jsx

import api from "@/api/client";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import EventDetail from "../components/events/EventDetail";
import { useEvent } from "../hooks/useEvents";

export default function EventDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { data, isLoading } = useEvent(slug);
  const [registering, setRegistering] = useState(false);

  const handleRegister = async (eventId) => {
    console.log("Registering for event:", eventId);

    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
      toast({
        title: "Login Required",
        description: "Please login to register for events",
        variant: "destructive",
      });
      navigate('/auth'); // Redirect to login page
      return;
    }

    setRegistering(true);

    try {
      // Call the registration API
      const response = await api.post('/registrations/', {
        event: eventId,
      });

      console.log("Registration successful:", response.data);

      toast({
        title: "Success! 🎉",
        description: "You're registered for this event!",
      });

      // Optionally redirect to "My Events" or refresh the page
      // navigate('/my-events');

    } catch (error) {
      console.error("Registration error:", error.response?.data);

      // Handle specific error messages
      const errorMsg = error.response?.data?.event?.[0] 
        || error.response?.data?.detail 
        || error.response?.data?.attendee?.[0]
        || "Failed to register. Please try again.";

      toast({
        title: "Registration Failed",
        description: errorMsg,
        variant: "destructive",
      });

    } finally {
      setRegistering(false);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (!data) return <div>Not Found</div>;

  return (
    <EventDetail 
      event={data} 
      onRegister={handleRegister}  // ✅ Pass the handler!
    />
  );
}