/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        noc: {
          bg: '#000000',
          panel: '#0D0D0D',
          card: '#141414',
          border: '#262626',
          white: '#FFFFFF',
          silver: '#E5E5E5',
          muted: '#737373',
          dark: '#1C1C1C',
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
