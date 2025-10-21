import { Calendar, Users, Layers, Home, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useLocation, Link } from "react-router-dom";

const navItems = [
  { label: "Dashboard", icon: Home, to: "/" },
  { label: "Events", icon: Calendar, to: "/events" },
  { label: "Sessions", icon: Layers, to: "/sessions" },
  { label: "Attendees", icon: Users, to: "/attendees" },
];

export function Sidebar() {
  const { pathname } = useLocation();

  return (
    <aside className="w-64 bg-white shadow-sidebar flex flex-col">
      <div className="px-6 py-4 border-b border-gray-100">
        <h1 className="text-xl font-bold text-brand-600">EventHub</h1>
        <p className="text-xs text-gray-500">Management Platform</p>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        {navItems.map((item) => {
          const active = pathname.startsWith(item.to);
          const Icon = item.icon;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                "flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium",
                active
                  ? "bg-brand-50 text-brand-600"
                  : "text-gray-600 hover:bg-gray-100"
              )}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <div className="bg-brand-50 rounded-lg p-3">
          <p className="text-xs text-gray-700 font-medium">Need Help?</p>
          <p className="text-xs text-gray-500">Check out our documentation</p>
          <Button variant="default" size="sm" className="w-full mt-2">
            <HelpCircle className="h-4 w-4 mr-2" /> View Docs
          </Button>
        </div>
      </div>
    </aside>
  );
}
