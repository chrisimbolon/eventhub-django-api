// components/DateTimePicker.jsx

import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

export default function DateTimePicker({ value, onChange }) {
  const date = value ? new Date(value) : null;

  const handleDateChange = (selectedDate) => {
    if (!selectedDate) return;

    const newDate = new Date(selectedDate);

    if (date) {
      newDate.setHours(date.getHours());
      newDate.setMinutes(date.getMinutes());
    }

    onChange(newDate.toISOString());
  };

  const handleTimeChange = (e) => {
    if (!date) return;

    const [hours, minutes] = e.target.value.split(":");

    const newDate = new Date(date);
    newDate.setHours(hours);
    newDate.setMinutes(minutes);

    onChange(newDate.toISOString());
  };

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className="w-full justify-start text-left font-normal"
        >
          <CalendarIcon className="mr-2 h-4 w-4" />

          {date ? (
            format(date, "dd MMM yyyy, HH:mm")
          ) : (
            <span className="text-muted-foreground">
              Pick date & time
            </span>
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-auto p-4 space-y-3">
        {/* 📅 Calendar */}
        <Calendar
          mode="single"
          selected={date}
          onSelect={handleDateChange}
        />

        {/* ⏰ Time Picker */}
        <input
          type="time"
          className="border rounded px-2 py-1 w-full"
          value={
            date
              ? `${String(date.getHours()).padStart(2, "0")}:${String(
                  date.getMinutes()
                ).padStart(2, "0")}`
              : ""
          }
          onChange={handleTimeChange}
        />
      </PopoverContent>
    </Popover>
  );
}