// frontend/vite.config.js

import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  
  server: {
    host: true,
    port: 5173,
  },
  
  preview: {
    host: "0.0.0.0",
    port: 4173,
    strictPort: true,
    // ✅ CRITICAL: Disable host check
    cors: true,
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
});