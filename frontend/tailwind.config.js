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
        dark: {
          950: '#06080e',
          900: '#0b0f19',
          850: '#111726',
          800: '#161f33',
          700: '#23304d',
          600: '#32456e',
        },
        cyber: {
          blue: '#00d2ff',
          indigo: '#4f46e5',
          purple: '#9333ea',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
          crimson: '#e11d48',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

