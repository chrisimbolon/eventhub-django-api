import React from "react";
import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="w-64 hidden md:block border-r bg-white">
      <div className="p-4">
        <nav className="space-y-2">
          <Link to="/" className="block py-2 px-3 rounded hover:bg-gray-100">Home</Link>
          <Link to="/events" className="block py-2 px-3 rounded hover:bg-gray-100">Events</Link>
          <Link to="/admin" className="block py-2 px-3 rounded hover:bg-gray-100">Admin</Link>
        </nav>
      </div>
    </aside>
  );
}
