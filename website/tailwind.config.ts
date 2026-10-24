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
        display: ["var(--font-manrope)", "var(--font-inter)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-lg": ["3.25rem", { lineHeight: "1.08", letterSpacing: "-0.035em", fontWeight: "800" }],
        "display": ["2.5rem", { lineHeight: "1.12", letterSpacing: "-0.03em", fontWeight: "700" }],
        "title": ["1.375rem", { lineHeight: "1.3", letterSpacing: "-0.02em", fontWeight: "600" }],
        "body-lg": ["1.125rem", { lineHeight: "1.65", letterSpacing: "-0.01em" }],
        "body": ["1rem", { lineHeight: "1.65", letterSpacing: "-0.006em" }],
        "caption": ["0.8125rem", { lineHeight: "1.5", letterSpacing: "0.01em" }],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        ink: {
          DEFAULT: "var(--ink)",
          muted: "var(--ink-muted)",
          subtle: "var(--ink-subtle)",
        },
        brand: {
          50: "#f4f3ff",
          100: "#eceafd",
          200: "#dcd8fc",
          300: "#c2bbf8",
          400: "#9d92f0",
          500: "#7568e3",
          600: "#5b4ed0",
          700: "#4a3fb5",
          800: "#3f3693",
          900: "#362f76",
        },
        telegram: {
          DEFAULT: "#2a9fd6",
          dark: "#2288b8",
          soft: "#e8f6fc",
        },
        surface: {
          DEFAULT: "#ffffff",
          muted: "#f3f4f8",
          elevated: "#fafbfc",
        },
        line: {
          DEFAULT: "var(--line)",
          strong: "var(--line-strong)",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 8px 24px -6px rgba(15, 23, 42, 0.07)",
        "card-hover":
          "0 2px 4px rgba(15, 23, 42, 0.04), 0 16px 40px -8px rgba(91, 78, 208, 0.12)",
        mockup: "0 24px 48px -12px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(15, 23, 42, 0.04)",
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(ellipse 85% 55% at 50% -15%, rgba(117, 104, 227, 0.11), transparent 55%), radial-gradient(ellipse 45% 35% at 100% 5%, rgba(42, 159, 214, 0.08), transparent), radial-gradient(ellipse 40% 40% at 0% 25%, rgba(157, 146, 240, 0.07), transparent)",
        "cta-gradient":
          "linear-gradient(145deg, #4a3fb5 0%, #5b4ed0 42%, #2a7fb0 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
