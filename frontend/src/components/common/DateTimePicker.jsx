// src/components/common/DateTimePicker.jsx
// Works on Chrome + Safari — input covers entire clickable area perfectly

import { Calendar } from "lucide-react"
import { useRef } from "react"

export default function DateTimePicker({ value, onChange, placeholder = "Pilih tanggal & waktu" }) {
  const inputRef = useRef(null)

  const toLocalFormat = (isoString) => {
    if (!isoString) return ""
    try {
      const d = new Date(isoString)
      const pad = (n) => String(n).padStart(2, "0")
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
    } catch { return "" }
  }

  const handleChange = (e) => {
    if (!e.target.value) { onChange(""); return }
    onChange(new Date(e.target.value).toISOString())
  }

  const formatDisplay = (isoString) => {
    if (!isoString) return null
    try {
      return new Date(isoString).toLocaleString("id-ID", {
        day: "numeric", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      })
    } catch { return null }
  }

  const displayValue = formatDisplay(value)

  return (
    <div className="relative w-full h-10">
      {/* Visual layer — behind */}
      <div className="flex items-center gap-2 h-10 px-3 w-full rounded-lg border border-input
                      bg-background text-sm hover:border-slate-400 transition-all select-none
                      pointer-events-none absolute inset-0">
        <Calendar size={15} className="text-slate-400 shrink-0" />
        <span className={`flex-1 ${displayValue ? "text-slate-700" : "text-slate-400"}`}>
          {displayValue || placeholder}
        </span>
      </div>

      {/* Native input — sits exactly on top, fully transparent, handles all clicks */}
      <input
        ref={inputRef}
        type="datetime-local"
        value={toLocalFormat(value)}
        onChange={handleChange}
        style={{ colorScheme: "light", opacity: 0 }}
        className="absolute inset-0 w-full h-full cursor-pointer z-10"
      />
    </div>
  )
}
