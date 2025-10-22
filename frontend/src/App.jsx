// src/App.js

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import Sidebar from "./components/layout/Sidebar";
import Footer from "./components/layout/Footer";
import Home from "./pages/Home";
import EventsPage from "./pages/EventsPage";
import EventDetailPage from "./pages/EventDetailPage";
import AuthPage from "./pages/AuthPage";
import AdminPage from "./pages/AdminPage";
import CreateEvent from "./pages/CreateEvent";
import { useAuth } from "./hooks/useAuth";

export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:id" element={<EventDetailPage />} />
            <Route
              path="/admin/*"
              element={user?.is_admin ? <AdminPage /> : <Navigate to="/" replace />}
            />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/create-event" element={<CreateEvent />} />
            <Route path="*" element={<div>Not Found</div>} />
          </Routes>
        </main>
      </div>
      <Footer />
    </div>
  );
}
