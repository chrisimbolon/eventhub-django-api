// src/components/layout/Sidebar.jsx
import { useAuth } from "@/hooks/useAuth";
import {
  BarChart3,
  Building2,
  CalendarDays,
  ChevronRight,
  FileText,
  Home,
  LayoutDashboard,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  {
    label: "Main",
    items: [
      { to: "/", icon: Home, label: "Home" },
      { to: "/events", icon: CalendarDays, label: "Events" },
    ],
  },
  {
    label: "MICE",
    items: [
      { to: "/mice/projects", icon: Building2, label: "Projects" },
    ],
    requiresAuth: true,
  },
  {
    label: "Admin",
    items: [
      { to: "/admin", icon: ShieldCheck, label: "Admin Panel" },
    ],
    requiresAdmin: true,
  },
];

function NavItem({ to, icon: Icon, label, active }) {
  return (
    <Link
      to={to}
      className={`
        flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
        transition-all duration-150 group
        ${active
          ? "bg-slate-900 text-white shadow-sm"
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        }
      `}
    >
      <Icon
        size={16}
        className={active ? "text-white" : "text-slate-400 group-hover:text-slate-600"}
      />
      <span>{label}</span>
      {active && (
        <ChevronRight size={12} className="ml-auto text-slate-400" />
      )}
    </Link>
  );
}

export default function Sidebar() {
  const location = useLocation();
  const { user, isAdmin } = useAuth();

  return (
    <aside className="w-60 hidden md:flex flex-col border-r bg-white min-h-screen shrink-0">
      {/* Brand accent bar */}
      <div className="h-1 bg-gradient-to-r from-slate-800 via-slate-600 to-slate-400" />

      <div className="flex-1 p-4 space-y-6 overflow-y-auto">
        {NAV_ITEMS.map((group) => {
          if (group.requiresAuth && !user) return null;
          if (group.requiresAdmin && !isAdmin) return null;

          return (
            <div key={group.label}>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2 px-3">
                {group.label}
              </p>
              <div className="space-y-0.5">
                {group.items.map((item) => (
                  <NavItem
                    key={item.to}
                    {...item}
                    active={
                      item.to === "/"
                        ? location.pathname === "/"
                        : location.pathname.startsWith(item.to)
                    }
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom user info */}
      {user && (
        <div className="p-4 border-t">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-slate-50">
            <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center text-white text-xs font-bold shrink-0">
              {user.name?.[0]?.toUpperCase() || user.username?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-800 truncate">
                {user.name || user.username}
              </p>
              <p className="text-xs text-slate-400 truncate">{user.email}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
