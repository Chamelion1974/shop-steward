/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // The Hub brand colors
        hub: {
          primary: '#2563eb',    // Blue
          secondary: '#7c3aed',  // Purple
          accent: '#f59e0b',     // Amber
          success: '#10b981',    // Green
          warning: '#f59e0b',    // Amber
          danger: '#ef4444',     // Red
          dark: '#1e293b',       // Slate 800
          light: '#f8fafc',      // Slate 50
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
      }
    },
  },
  plugins: [],
}
