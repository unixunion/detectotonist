/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,js,vue}'],
  theme: {
    extend: {},
  },
  plugins: [
      require('daisyui'),
  ],
}

