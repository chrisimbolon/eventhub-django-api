import React, { useState } from "react";

export default function EventFilters({ onChange }) {
  const [q, setQ] = useState("");
  const [tag, setTag] = useState("");

  const submit = (e) => {
    e.preventDefault();
    onChange({ q, tag });
  };

  return (
    <form onSubmit={submit} className="bg-white p-3 rounded shadow-sm">
      <div className="flex gap-2">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search events" className="flex-1 px-3 py-2 border rounded" />
        <input value={tag} onChange={e => setTag(e.target.value)} placeholder="Tag" className="w-40 px-3 py-2 border rounded" />
        <button className="px-3 py-2 bg-blue-600 text-white rounded">Filter</button>
      </div>
    </form>
  );
}
