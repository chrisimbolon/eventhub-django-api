import React from "react";

export default function Button({ children, className = "", ...props }) {
  return (
    <button
      className={`px-4 py-2 rounded-md text-sm font-medium transition hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
