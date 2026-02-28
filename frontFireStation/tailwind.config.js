/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "flowbite/plugin",
    "../node_modules/flowbite",
    "./src/**/*.{vue,js,ts,jsx,tsx,html}",
  ],
  theme: {
    extend: {
      width: {
        10: "10%",
        12: "12%",
        14: "14%",
        15: "15%",

        20: "20%",
        30: "30%",
        40: "40%",
        50: "50%",
        60: "60%",
        70: "70%",
        80: "80%",
        90: "90%",
        100: "100%",
        110: "110%",
        120: "120%",
        130: "130%",
        140: "140%",
        150: "150%",
        200: "200%",
      },
      colors: {
        primary: "#3b82f6", // синий
        secondary: "#64748b", // серый
        error: "#ef4444", // красный
        success: "#22c55e", // зеленый
        dark: "#1f2937",
      },
      // тень на кнопки
      boxShadow: {
        intense: "0 8px 15px rgba(0,0,0,0.22)",
      },
    },
    screens: {
      xs: "480px",
      sm: "640px",
      md: "768px",
      lgg: "900px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
      "3xl": "2560px",
    },
  },
  plugins: [require("flowbite/plugin")],
};
