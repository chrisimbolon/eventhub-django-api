// External libraries
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

// Internal hooks
import { useAuth } from "../../hooks/useAuth";

// Components
import LanguageSwitcher from "@/components/common/LanguageSwitcher";
import LogoutButton from "./LogoutButton";

export default function Navbar() {
  const { t } = useTranslation("common");
  const { user, loading, isAdmin } = useAuth();

  const showAdminLink = !loading && user && isAdmin;
  const isAuthenticated = !loading && user;

  return (
    <header className="bg-white border-b">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div className="text-2xl font-extrabold">Eventhub</div>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-4">
          <Link to="/events" className="text-sm hover:underline">
            {t("nav.events")}
          </Link>

          {showAdminLink && (
            <Link to="/admin" className="text-sm hover:underline">
              {t("nav.admin")}
            </Link>
          )}

          {isAuthenticated ? (
            <>
              <div className="text-sm text-gray-700 hidden sm:block">
                {t("nav.hi")}, {user.name}
              </div>
              <LogoutButton />
            </>
          ) : (
            <Link to="/auth" className="text-sm hover:underline">
              {t("nav.login")}
            </Link>
          )}

          {/* Language Switcher - Far Right */}
          <LanguageSwitcher />
        </nav>
      </div>
    </header>
  );
}