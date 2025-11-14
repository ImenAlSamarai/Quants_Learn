/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Claude-inspired color palette
        cream: {
          50: '#FDFCFB',
          100: '#FAF9F6',
          200: '#F5F4F1',
          300: '#E5E5E0',
          400: '#D4D4CF',
        },
        slate: {
          50: '#F8F8F7',
          100: '#9B9B9B',
          200: '#6B6B6B',
          300: '#4A4A4A',
          400: '#2A2A2A',
          500: '#1A1A1A',
        },
        gold: {
          100: '#E6D4B0',
          200: '#D9C39D',
          300: '#C9A96E',
          400: '#B8935A',
          500: '#A67D48',
        },
        // Muted node colors
        sage: {
          100: '#C8D8CF',
          200: '#A5C4B5',
          300: '#7BA591',
          400: '#5F8A73',
        },
        ocean: {
          100: '#B8D3E8',
          200: '#8FB8D9',
          300: '#6B9BD1',
          400: '#5082B8',
        },
        lavender: {
          100: '#D4CDE3',
          200: '#B8AFCC',
          300: '#9B8FB5',
          400: '#7E739E',
        },
        tan: {
          100: '#EDD9C3',
          200: '#E0C49F',
          300: '#D4A574',
          400: '#C18D56',
        },
        terracotta: {
          100: '#E6BDB5',
          200: '#D99E93',
          300: '#C17B6C',
          400: '#A8604F',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['SF Mono', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [],
}
