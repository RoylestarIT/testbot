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
        display: ["var(--font-onest)", "var(--font-inter)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-lg": [
          "3.125rem",
          { lineHeight: "1.06", letterSpacing: "-0.032em", fontWeight: "800" },
        ],
        display: [
          "2.375rem",
          { lineHeight: "1.14", letterSpacing: "-0.028em", fontWeight: "700" },
        ],
        title: [
          "1.3125rem",
          { lineHeight: "1.32", letterSpacing: "-0.018em", fontWeight: "600" },
        ],
        "body-lg": ["1.0625rem", { lineHeight: "1.68", letterSpacing: "-0.008em" }],
        body: ["1rem", { lineHeight: "1.68", letterSpacing: "-0.004em" }],
        caption: ["0.8125rem", { lineHeight: "1.52", letterSpacing: "0.005em" }],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        ink: {
          DEFAULT: "var(--ink)",
          muted: "var(--ink-muted)",
          subtle: "var(--ink-subtle)",
          faint: "var(--ink-faint)",
        },
        brand: {
          50: "#f3f2fb",
          100: "#eae8f8",
          200: "#d5d1f0",
          300: "#b8b1e4",
          400: "#9489d4",
          500: "#7266c4",
          600: "#5a4fb3",
          700: "#4a4196",
          800: "#3f377a",
          900: "#363065",
        },
        success: {
          DEFAULT: "#2d9a6f",
          soft: "#e8f5ef",
          muted: "#c5e6d6",
        },
        telegram: {
          DEFAULT: "#2a9fd6",
          dark: "#2288b8",
          soft: "#e8f6fc",
        },
        surface: {
          DEFAULT: "var(--surface)",
          muted: "var(--surface-muted)",
          elevated: "var(--surface-elevated)",
        },
        line: {
          DEFAULT: "var(--line)",
          strong: "var(--line-strong)",
        },
        footer: {
          bg: "var(--footer-bg)",
          border: "var(--footer-border)",
          text: "var(--footer-text)",
          muted: "var(--footer-muted)",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(22, 28, 45, 0.035), 0 10px 28px -8px rgba(22, 28, 45, 0.08)",
        "card-hover":
          "0 2px 4px rgba(22, 28, 45, 0.04), 0 18px 44px -10px rgba(90, 79, 179, 0.14)",
        mockup: "0 24px 48px -12px rgba(22, 28, 45, 0.16), 0 0 0 1px rgba(22, 28, 45, 0.05)",
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(ellipse 90% 60% at 50% -20%, rgba(114, 102, 196, 0.09), transparent 58%), radial-gradient(ellipse 50% 40% at 100% 0%, rgba(42, 159, 214, 0.06), transparent), radial-gradient(ellipse 45% 45% at -5% 30%, rgba(148, 137, 212, 0.05), transparent)",
        "cta-gradient":
          "linear-gradient(152deg, #3f377a 0%, #5a4fb3 48%, #2878a3 100%)",
        "section-fade": "linear-gradient(180deg, var(--surface-muted) 0%, var(--background) 100%)",
      },
    },
  },
  plugins: [],
} satisfies Config;
