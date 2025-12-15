/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ambedkar': {
          50: '#f0f9ff',
          100: '#e0f2fe',  // Very Light Blue
          500: '#0ea5e9',  // Primary Brand Color
          800: '#075985',  // Dark Intellectual Blue
          900: '#0c4a6e',  // Almost Black Blue
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}