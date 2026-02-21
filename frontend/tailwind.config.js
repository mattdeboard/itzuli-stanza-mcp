/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Soothing professional palette inspired by nature and tranquility
        sage: {
          50: '#f8faf9',
          100: '#e8f2ec',
          200: '#d1e5d8',
          300: '#a8d0b8',
          400: '#7bb394',
          500: '#5a9975',
          600: '#477c5d',
          700: '#3a634b',
          800: '#314f3d',
          900: '#2a4234',
        },
        // Light tan/hay background palette
        tan: {
          25: '#fefcfa',
          50: '#fdf8f3',
          100: '#fbf1e8',
          200: '#f6e4d1',
          300: '#f0d5b8',
          400: '#e8c19f',
          500: '#daa973',
          600: '#c8954d',
          700: '#a67c41',
          800: '#7d5d31',
          900: '#5a4423',
        },
        slate: {
          25: '#fdfefe',
          50: '#f9fafb',
          100: '#f3f5f7',
          150: '#eaecef',
          200: '#e1e4e8',
          300: '#d0d7de',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#0f172a',
        },
        accent: {
          mint: '#4ade80',
          teal: '#14b8a6',
          warm: '#f59e0b',
        },
        ribbon: {
          primary: '#5a9975',
          secondary: '#7bb394',
          accent: '#14b8a6',
        },
      },
      spacing: {
        'ribbon-space': '140px',
        '18': '4.5rem',
        '22': '5.5rem',
      },
      fontFamily: {
        'display': ['Crimson Pro', 'serif'],
        'sans': ['Source Sans 3', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Monaco', 'monospace'],
      },
      opacity: {
        '15': '0.15',
        '85': '0.85',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'ribbon-draw': 'ribbon-draw 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        'token-highlight': 'token-highlight 0.15s ease-out',
        'fade-in': 'fade-in 0.6s ease-out',
        'slide-up': 'slide-up 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
        'gentle-pulse': 'gentle-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        'ribbon-draw': {
          '0%': { strokeDasharray: '1000', strokeDashoffset: '1000', opacity: '0.3' },
          '100%': { strokeDasharray: '1000', strokeDashoffset: '0', opacity: '0.8' },
        },
        'token-highlight': {
          '0%': { transform: 'translateY(0px)', boxShadow: '0 0 0 0 rgba(90, 153, 117, 0)' },
          '100%': { transform: 'translateY(-1px)', boxShadow: '0 2px 8px 0 rgba(90, 153, 117, 0.15)' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0px)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0px)' },
        },
        'gentle-pulse': {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '0.8' },
        },
      },
    },
  },
  plugins: [],
}