/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ribbon: {
          blue: '#3498db',
          'blue-hover': '#2980b9',
        },
      },
      spacing: {
        'ribbon-space': '120px',
      },
      opacity: {
        '15': '0.15',
      },
      animation: {
        'ribbon-draw': 'ribbon-draw 0.3s ease-out',
        'token-highlight': 'token-highlight 0.2s ease-out',
      },
      keyframes: {
        'ribbon-draw': {
          '0%': { strokeDasharray: '1000', strokeDashoffset: '1000' },
          '100%': { strokeDasharray: '1000', strokeDashoffset: '0' },
        },
        'token-highlight': {
          '0%': { transform: 'translateY(0px)' },
          '100%': { transform: 'translateY(-2px)' },
        },
      },
    },
  },
  plugins: [],
}