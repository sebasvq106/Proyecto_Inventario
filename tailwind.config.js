/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./managment_system/**/*.{html,js}",
    "./node_modules/tw-elements/js/**/*.js",
  ],
  theme: {
    extend: {},
  },
  darkMode: "class",
  plugins: [require("tw-elements/plugin.cjs")],
};