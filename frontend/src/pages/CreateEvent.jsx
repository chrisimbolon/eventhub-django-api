// src/pages/CreateEvent.jsx

import { createEvent } from "@/api/events";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { ArrowLeft, Calendar as CalendarIcon } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

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
    startHour: "09",
    startMinute: "00",
    endHour: "17",
    endMinute: "00",
  });

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Generate hours (00-23) and minutes (00, 15, 30, 45)
  const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'));
  const minutes = ['00', '15', '30', '45'];

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!date) {
      toast({
        title: "Missing date",
        description: "Please select a valid start date.",
        variant: "destructive",
      });
      return;
    }

    // Construct time strings from dropdowns
    const startTime = `${formData.startHour}:${formData.startMinute}`;
    const endTime = `${formData.endHour}:${formData.endMinute}`;

    const payload = {
      title: formData.title,
      slug: formData.title.toLowerCase().replace(/\s+/g, "-"),
      description: formData.description,
      start_date: new Date(`${format(date, "yyyy-MM-dd")}T${startTime}:00Z`).toISOString(),
      end_date: new Date(`${format(date, "yyyy-MM-dd")}T${endTime}:00Z`).toISOString(),
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
        description: "Your event has been created and saved.",
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

      {/* Header - FIXED gradient text clipping */}
      <div className="mb-8">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent leading-tight pb-2">
          Create New Event
        </h1>
        <p className="text-lg text-muted-foreground">
          Fill in the details to create a new technical conference
        </p>
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
              <Label htmlFor="title" className="text-base font-medium">Event Title *</Label>
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
              <Label htmlFor="description" className="text-base font-medium">Description *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange("description", e.target.value)}
                placeholder="Describe your event..."
                required
                className="min-h-32 resize-none"
              />
            </div>

            {/* Date & Time - IMPROVED with dropdowns */}
            <div className="space-y-4">
              <Label className="text-base font-medium">Date & Time *</Label>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Date Picker */}
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Event Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full h-12 justify-start text-left font-normal",
                          !date && "text-muted-foreground"
                        )}
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

                {/* Start Time */}
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">Start Time</Label>
                  <div className="flex gap-2">
                    <Select value={formData.startHour} onValueChange={(val) => handleChange("startHour", val)}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="HH" />
                      </SelectTrigger>
                      <SelectContent>
                        {hours.map((h) => (
                          <SelectItem key={h} value={h}>{h}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <span className="flex items-center text-2xl font-bold">:</span>
                    <Select value={formData.startMinute} onValueChange={(val) => handleChange("startMinute", val)}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="MM" />
                      </SelectTrigger>
                      <SelectContent>
                        {minutes.map((m) => (
                          <SelectItem key={m} value={m}>{m}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* End Time */}
                <div className="space-y-2">
                  <Label className="text-sm text-muted-foreground">End Time</Label>
                  <div className="flex gap-2">
                    <Select value={formData.endHour} onValueChange={(val) => handleChange("endHour", val)}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="HH" />
                      </SelectTrigger>
                      <SelectContent>
                        {hours.map((h) => (
                          <SelectItem key={h} value={h}>{h}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <span className="flex items-center text-2xl font-bold">:</span>
                    <Select value={formData.endMinute} onValueChange={(val) => handleChange("endMinute", val)}>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="MM" />
                      </SelectTrigger>
                      <SelectContent>
                        {minutes.map((m) => (
                          <SelectItem key={m} value={m}>{m}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </div>

            {/* Venue & Capacity */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="venue" className="text-base font-medium">Venue Name *</Label>
                <Input
                  id="venue"
                  value={formData.venue}
                  onChange={(e) => handleChange("venue", e.target.value)}
                  placeholder="e.g., Convention Center"
                  required
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="capacity" className="text-base font-medium">Maximum Capacity *</Label>
                <Input
                  id="capacity"
                  type="number"
                  min="1"
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
              <Label htmlFor="address" className="text-base font-medium">Venue Address *</Label>
              <Input
                id="address"
                value={formData.address}
                onChange={(e) => handleChange("address", e.target.value)}
                placeholder="Full venue address"
                required
                className="h-12"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-4 pt-6 border-t">
              <Button
                type="submit"
                disabled={loading}
                className="gradient-primary text-white shadow-glow flex-1 h-12 text-base font-semibold"
              >
                {loading ? "Creating..." : "Create Event"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/events")}
                disabled={loading}
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