/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#7c3aed', // purple
          600: '#6d28d9',
          700: '#5b21b6',
        },
      },
      boxShadow: {
        sidebar: '4px 0 12px rgba(0,0,0,0.05)',
      },
    },
  },
  plugins: [],
}
