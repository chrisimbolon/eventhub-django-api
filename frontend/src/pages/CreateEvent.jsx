// src/pages/CreateEvent.jsx

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Calendar as CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { toast } from "@/hooks/use-toast";
import { createEvent } from "@/api/events";

export default function CreateEvent() {
  const navigate = useNavigate();
  const [date, setDate] = useState(null);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    venue: "",
    address: "",
    capacity: "",
    startTime: "",
    endTime: "",
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };


  const handleSubmit = async (e) => {
  e.preventDefault();

  if (!date) {
    toast({
      title: "Missing date",
      description: "Please select a valid start date.",
    });
    return;
  }

  const payload = {
    title: formData.title,
    slug: formData.title.toLowerCase().replace(/\s+/g, "-"),
    description: formData.description,
    start_date: new Date(`${format(date, "yyyy-MM-dd")}T${formData.startTime}:00Z`).toISOString(),
    end_date: new Date(`${format(date, "yyyy-MM-dd")}T${formData.endTime}:00Z`).toISOString(),
    registration_start: new Date().toISOString(),
    registration_end: new Date(`${format(date, "yyyy-MM-dd")}T00:00:00Z`).toISOString(),
    venue_name: formData.venue,
    venue_address: formData.address,
    city: "San Francisco", 
    country: "United States",
    capacity: parseInt(formData.capacity, 10),
  };

  try {
    setLoading(true);
    await createEvent(payload);

    toast({
      title: "Event Created Successfully!",
      description: "Your event has been created and saved in the database.",
    });

    setTimeout(() => navigate("/events"), 1500);
  } catch (error) {
    toast({
      title: "Error Creating Event",
      description:
        error.response?.data?.detail ||
        JSON.stringify(error.response?.data) ||
        "Failed to create event.",
      variant: "destructive",
    });
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen p-8 animate-fade-in">
      {/* Back Button */}
      <Link to="/events">
        <Button variant="ghost" className="mb-6 hover:text-primary">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Events
        </Button>
      </Link>

      {/* Header */}
      <div className="mb-8 relative">
        <div className="absolute inset-0 gradient-primary opacity-5 blur-3xl rounded-full" />
        <div className="relative">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            Create New Event
          </h1>
          <p className="text-lg text-muted-foreground">
            Fill in the details to create a new technical conference
          </p>
        </div>
      </div>

      {/* Form */}
      <Card className="glass-effect max-w-4xl">
        <CardHeader>
          <CardTitle className="text-2xl">Event Details</CardTitle>
          <CardDescription>Enter all the necessary information for your event</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title" className="text-base">Event Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleChange("title", e.target.value)}
                placeholder="e.g., React Summit 2025"
                required
                className="h-12"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-base">Description *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange("description", e.target.value)}
                placeholder="Describe your event..."
                required
                className="min-h-32"
              />
            </div>

            {/* Date & Time */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-base">Event Date *</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn("w-full h-12 justify-start text-left font-normal", !date && "text-muted-foreground")}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {date ? format(date, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar mode="single" selected={date} onSelect={setDate} initialFocus />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label htmlFor="startTime" className="text-base">Start Time *</Label>
                <Input
                  id="startTime"
                  type="time"
                  value={formData.startTime}
                  onChange={(e) => handleChange("startTime", e.target.value)}
                  required
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="endTime" className="text-base">End Time *</Label>
                <Input
                  id="endTime"
                  type="time"
                  value={formData.endTime}
                  onChange={(e) => handleChange("endTime", e.target.value)}
                  required
                  className="h-12"
                />
              </div>
            </div>

            {/* Venue & Capacity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="venue" className="text-base">Venue Name *</Label>
                <Input
                  id="venue"
                  value={formData.venue}
                  onChange={(e) => handleChange("venue", e.target.value)}
                  placeholder="e.g., San Francisco Convention Center"
                  required
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="capacity" className="text-base">Maximum Capacity *</Label>
                <Input
                  id="capacity"
                  type="number"
                  value={formData.capacity}
                  onChange={(e) => handleChange("capacity", e.target.value)}
                  placeholder="e.g., 500"
                  required
                  className="h-12"
                />
              </div>
            </div>

            {/* Address */}
            <div className="space-y-2">
              <Label htmlFor="address" className="text-base">Venue Address *</Label>
              <Input
                id="address"
                value={formData.address}
                onChange={(e) => handleChange("address", e.target.value)}
                placeholder="e.g., 747 Howard St, San Francisco, CA"
                required
                className="h-12"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-6">
              <Button
                type="submit"
                disabled={loading}
                className="gradient-primary text-white shadow-glow flex-1 h-12 text-base"
              >
                {loading ? "Creating..." : "Create Event"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/events")}
                className="flex-1 h-12 text-base"
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
