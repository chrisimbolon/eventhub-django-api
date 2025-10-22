import React from "react";
import { useAuth } from "../../hooks/useAuth";
import Button from "../common/Button";
import { useNavigate } from "react-router-dom";

export default function LogoutButton({ className = "" }) {
  const { logout } = useAuth();
  const nav = useNavigate();

  const handle = async () => {
    await logout();
    nav("/", { replace: true });
  };

  return (
    <Button onClick={handle} className={className || "bg-red-600 text-white"}>
      Logout
    </Button>
  );
}
