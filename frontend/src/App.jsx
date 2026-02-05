// src/App.js

import { Toaster } from "@/components/ui/toaster";
import { Navigate, Route, Routes } from "react-router-dom";
import Footer from "./components/layout/Footer";
import Navbar from "./components/layout/Navbar";
import Sidebar from "./components/layout/Sidebar";
import { useAuth } from "./hooks/useAuth";
import AdminPage from "./pages/AdminPage";
import AuthPage from "./pages/AuthPage";
import CreateEvent from "./pages/CreateEvent";
import EventDetailPage from "./pages/EventDetailPage";
import EventsPage from "./pages/EventsPage";
import Home from "./pages/Home";


export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900">
      <Navbar />

      <Toaster />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/events" element={<EventsPage />} />
            {/* <Route path="/events/:id" element={<EventDetailPage />} /> */}
            <Route path="/events/:slug" element={<EventDetailPage />} />

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
