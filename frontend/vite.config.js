import react from '@vitejs/plugin-react'
import path from "path"
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  server: {
    host: true, // allow external access (0.0.0.0)
    allowedHosts: [
      'eventhub.chrisimbolon.dev',
      'localhost',
      '127.0.0.1'
    ]
  },

  preview: {
    allowedHosts: [
      'eventhub.chrisimbolon.dev',
      'localhost',
      '127.0.0.1'
    ]
  }
})
