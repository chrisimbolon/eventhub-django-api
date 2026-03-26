import { format } from "date-fns";
import { CalendarIcon, Clock } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

export default function DateTimePicker({ value, onChange }) {
  const date = value ? new Date(value) : null;
  const [open, setOpen] = useState(false);

  const hours = date ? date.getHours() : 9;
  const minutes = date ? date.getMinutes() : 0;

  // ── DATE CHANGE ───────────────────────────────────────
  const handleDateChange = (selectedDate) => {
    if (!selectedDate) return;

    const newDate = new Date(selectedDate);
    newDate.setHours(hours);
    newDate.setMinutes(minutes);

    onChange(newDate.toISOString());
  };

  // ── TIME CHANGE ───────────────────────────────────────
  const updateTime = (h, m) => {
    if (!date) return;

    const newDate = new Date(date);
    newDate.setHours(h);
    newDate.setMinutes(m);

    onChange(newDate.toISOString());
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className="w-full justify-start text-left font-normal hover:bg-slate-50"
        >
          <CalendarIcon className="mr-2 h-4 w-4 text-slate-500" />
          {date ? (
            format(date, "PPP • HH:mm")
          ) : (
            <span className="text-slate-400">Pick date & time</span>
          )}
        </Button>
      </PopoverTrigger>

      {/* 💎 TRUE PREMIUM PANEL */}
      <PopoverContent className="w-auto p-0 rounded-xl shadow-xl border overflow-hidden">
        <div className="flex">
          
          {/* 📅 CALENDAR */}
          <div className="p-3">
            <Calendar
              mode="single"
              selected={date}
              onSelect={handleDateChange}
              initialFocus
            />
          </div>

          {/* ⏰ TIME PANEL */}
          <div className="w-[120px] border-l bg-slate-50 p-3 flex flex-col">
            <div className="flex items-center gap-2 text-sm text-slate-600 mb-3">
              <Clock className="w-4 h-4" />
              Time
            </div>

            <div className="flex gap-2">
              {/* HOURS */}
              <select
                value={hours}
                onChange={(e) =>
                  updateTime(Number(e.target.value), minutes)
                }
                className="w-full border rounded-md px-2 py-1 text-sm bg-white"
              >
                {Array.from({ length: 24 }).map((_, i) => (
                  <option key={i} value={i}>
                    {String(i).padStart(2, "0")}
                  </option>
                ))}
              </select>

              {/* MINUTES */}
              <select
                value={minutes}
                onChange={(e) =>
                  updateTime(hours, Number(e.target.value))
                }
                className="w-full border rounded-md px-2 py-1 text-sm bg-white"
              >
                {[0, 15, 30, 45].map((m) => (
                  <option key={m} value={m}>
                    {String(m).padStart(2, "0")}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}