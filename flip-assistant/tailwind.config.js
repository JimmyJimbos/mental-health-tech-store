/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        amber: {
          50: '#fffaf0',
          100: '#fef3d9',
          200: '#fce3ab',
          300: '#f9cd6e',
          400: '#f4ac36',
          500: '#e8901a',
          600: '#c46f12',
          700: '#9c5413',
          800: '#7e4416',
          900: '#693916',
        },
        ink: {
          50: '#f5f6f7',
          100: '#e6e8eb',
          200: '#c7ccd3',
          300: '#9aa3ae',
          400: '#6b7280',
          500: '#4b5563',
          600: '#374151',
          700: '#1f2937',
          800: '#111827',
          900: '#0b0f16',
        },
      },
    },
  },
  plugins: [],
};
