import React from "react";

export default function HeroSection({ title = "Discover events" , subtitle = "Find the next loud thing" }) {
  return (
    <div className="rounded-lg p-6 bg-gradient-to-r from-slate-900 to-indigo-700 text-white">
      <h1 className="text-3xl font-extrabold">{title}</h1>
      <p className="mt-2 text-sm text-indigo-100">{subtitle}</p>
    </div>
  );
}
