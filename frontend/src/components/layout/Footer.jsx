import React from "react";

export default function Footer() {
  return (
    <footer className="bg-white border-t mt-8">
      <div className="container mx-auto px-4 py-4 text-sm text-gray-500">
        © {new Date().getFullYear()} Eventhub — built with lots of Coffee 🤘
      </div>
    </footer>
  );
}
