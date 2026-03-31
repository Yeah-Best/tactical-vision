/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ink-dark': '#1A1A2E',
        'ink-darker': '#16213E',
        'gold-primary': '#C9A227',
        'gold-light': '#E8D5B7',
        'bg-deep': '#0D1117',
        'bg-dark': '#161B22',
        'bg-ink': '#1C2333',
        'text-primary': '#E6EDF3',
        'text-secondary': '#8B949E',
      },
      fontFamily: {
        'sans': ['Noto Sans SC', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'typing': 'typing 2s steps(40, end)',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        typing: {
          'from': { width: '0' },
          'to': { width: '100%' },
        },
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
