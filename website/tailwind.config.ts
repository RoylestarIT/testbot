import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        brand: {
          50: "#f5f3ff",
          100: "#ede9fe",
          200: "#ddd6fe",
          300: "#c4b5fd",
          400: "#a78bfa",
          500: "#7c6cf0",
          600: "#6356e8",
          700: "#5346d4",
          800: "#4538ad",
          900: "#3b3189",
        },
        telegram: {
          DEFAULT: "#24a1de",
          dark: "#1c8cc4",
        },
        surface: {
          DEFAULT: "#ffffff",
          muted: "#f4f6fb",
        },
      },
      boxShadow: {
        card: "0 4px 24px -4px rgba(15, 23, 42, 0.08), 0 2px 8px -2px rgba(15, 23, 42, 0.04)",
        "card-hover":
          "0 12px 40px -8px rgba(99, 86, 232, 0.15), 0 4px 16px -4px rgba(15, 23, 42, 0.06)",
        mockup: "0 25px 50px -12px rgba(15, 23, 42, 0.25)",
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(ellipse 80% 60% at 50% -10%, rgba(124, 108, 240, 0.18), transparent), radial-gradient(ellipse 50% 40% at 100% 0%, rgba(36, 161, 222, 0.12), transparent), radial-gradient(ellipse 40% 50% at 0% 20%, rgba(167, 139, 250, 0.1), transparent)",
        "cta-gradient": "linear-gradient(135deg, #5346d4 0%, #24a1de 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
