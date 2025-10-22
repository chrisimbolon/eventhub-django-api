import React from "react";

export default function EventsTable({ events = [], onEdit = () => {}, onDelete = () => {}, onExport = () => {} }) {
  return (
    <div className="bg-white rounded shadow overflow-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="p-3 text-left">Title</th>
            <th className="p-3 text-left">Date</th>
            <th className="p-3 text-left">Capacity</th>
            <th className="p-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {events.map(ev => (
            <tr key={ev.id} className="border-t">
              <td className="p-3">{ev.title}</td>
              <td className="p-3">{new Date(ev.start_date).toLocaleDateString()}</td>
              <td className="p-3">{ev.capacity}</td>
              <td className="p-3 space-x-2">
                <button onClick={() => onEdit(ev)}>Edit</button>
                <button onClick={() => onDelete(ev.id)}>Delete</button>
                <button onClick={() => onExport(ev.id)}>Export</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
