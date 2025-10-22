import React from "react";

export default function CapacityBar({ value = 0, max = 100 }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  let color = "bg-green-500";
  if (pct > 75) color = "bg-red-500";
  else if (pct > 50) color = "bg-amber-500";

  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{value} / {max}</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded">
        <div className={`${color} h-2 rounded`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
