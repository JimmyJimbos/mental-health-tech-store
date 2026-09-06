/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#f4f7f4',
          100: '#e5ebe4',
          200: '#c9d6c6',
          300: '#a3b89e',
          400: '#7c9975',
          500: '#5e7d57',
          600: '#496343',
          700: '#3c5038',
          800: '#32412f',
          900: '#2b3729',
        },
      },
    },
  },
  plugins: [],
};
