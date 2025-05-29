/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4a9eff',
        secondary: '#1e3c72',
        dark: '#0a0e27',
      }
    },
  },
  plugins: [],
}
