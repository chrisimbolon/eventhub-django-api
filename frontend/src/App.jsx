// src/App.jsx
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

// MICE pages
import MICEProjectsPage from "./pages/MICEProjectsPage";
import MICEProjectDetailPage from "./pages/MICEProjectDetailPage";
import QuotationBuilderPage from "./pages/QuotationBuilderPage";
import ClientPortalPage from "./pages/ClientPortalPage";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-800" />
    </div>
  );
  return user ? children : <Navigate to="/auth" replace />;
}

export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900">
      <Navbar />
      <Toaster />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 min-w-0">
          <Routes>
            {/* Existing routes */}
            <Route path="/" element={<Home />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/:slug" element={<EventDetailPage />} />
            <Route
              path="/admin/*"
              element={user?.is_admin ? <AdminPage /> : <Navigate to="/" replace />}
            />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/create-event" element={<CreateEvent />} />

            {/* MICE routes — all protected */}
            <Route
              path="/mice/projects"
              element={<ProtectedRoute><MICEProjectsPage /></ProtectedRoute>}
            />
            <Route
              path="/mice/projects/:projectId"
              element={<ProtectedRoute><MICEProjectDetailPage /></ProtectedRoute>}
            />
            <Route
              path="/mice/quotation/:quotationId"
              element={<ProtectedRoute><QuotationBuilderPage /></ProtectedRoute>}
            />

            {/* Client portal — PUBLIC, no auth, no sidebar */}
            <Route path="/quotation/portal/:token" element={<ClientPortalPage />} />

            <Route path="*" element={<div className="text-center py-20 text-slate-400">Page not found</div>} />
          </Routes>
        </main>
      </div>
      <Footer />
    </div>
  );
}
