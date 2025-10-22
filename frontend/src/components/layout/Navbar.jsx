import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import LogoutButton from "./LogoutButton";

export default function Navbar() {
  const { user, loading, isAdmin } = useAuth();

  return (
    <header className="bg-white border-b">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="text-2xl font-extrabold">Eventhub</div>
        </Link>

        <nav className="flex items-center gap-4">
          <Link to="/events" className="text-sm hover:underline">Events</Link>

          {!loading && user && isAdmin && (
            <Link to="/admin" className="text-sm hover:underline">Admin</Link>
          )}

          {!loading && user ? (
            <>
              <div className="text-sm text-gray-700 hidden sm:block">Hi, {user.name}</div>
              <LogoutButton />
            </>
          ) : (
            <Link to="/auth" className="text-sm hover:underline">Login</Link>
          )}
        </nav>
      </div>
    </header>
  );
}
