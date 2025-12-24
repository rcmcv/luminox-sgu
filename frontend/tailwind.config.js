/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx,js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e3f2ff',
          100: '#b3daff',
          200: '#81c2ff',
          300: '#4fa9ff',
          400: '#1d91ff',
          500: '#0377e6',
          600: '#005cb4',
          700: '#004182',
          800: '#002751',
          900: '#000e21',
        },
      },
    },
  },
  plugins: [],
};
