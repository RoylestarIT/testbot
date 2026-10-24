import type { Config } from "tailwindcss";

/**
 * Шкала заголовков — Major Third (×1.25) от 16px:
 * 20 → 25 → 31.25 → 39 → 48.8 → 61
 */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-body)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-body)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-xl": ["3.815rem", { lineHeight: "1.04", letterSpacing: "-0.035em", fontWeight: "600" }],
        "display-lg": ["3.052rem", { lineHeight: "1.08", letterSpacing: "-0.03em", fontWeight: "600" }],
        display: ["2.441rem", { lineHeight: "1.12", letterSpacing: "-0.025em", fontWeight: "600" }],
        headline: ["1.953rem", { lineHeight: "1.2", letterSpacing: "-0.02em", fontWeight: "600" }],
        title: ["1.25rem", { lineHeight: "1.35", letterSpacing: "-0.012em", fontWeight: "600" }],
        "body-lg": ["1.125rem", { lineHeight: "1.7", letterSpacing: "-0.003em" }],
        body: ["1rem", { lineHeight: "1.65" }],
        small: ["0.875rem", { lineHeight: "1.55" }],
        caption: ["0.8rem", { lineHeight: "1.5", letterSpacing: "0.01em" }],
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
          50: "#f1f6f5",
          100: "#e0ebe8",
          200: "#c1d6d1",
          300: "#94b8b0",
          400: "#62958b",
          500: "#3f786e",
          600: "#2c6359",
          700: "#215149",
          800: "#1b423c",
          900: "#163430",
        },
        clay: {
          50: "#fbf5ee",
          100: "#f4e6d4",
          300: "#e0b688",
          500: "#c1803f",
          600: "#a76a30",
        },
        success: {
          DEFAULT: "#2f7a5c",
          soft: "#eaf4ef",
          muted: "#cfe5da",
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
      maxWidth: {
        prose: "38rem",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        xs: "0 1px 2px rgba(20, 24, 22, 0.05)",
        card: "0 1px 2px rgba(20, 24, 22, 0.04), 0 4px 16px -6px rgba(20, 24, 22, 0.06)",
        "card-hover":
          "0 2px 4px rgba(20, 24, 22, 0.04), 0 20px 40px -16px rgba(22, 52, 48, 0.18)",
        button: "0 1px 2px rgba(22, 52, 48, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.12)",
        "button-hover": "0 8px 20px -8px rgba(22, 52, 48, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.14)",
        mockup: "0 40px 80px -32px rgba(20, 30, 28, 0.35), 0 0 0 1px rgba(20, 24, 22, 0.06)",
      },
      backgroundImage: {
        "hero-mesh":
          "radial-gradient(ellipse 70% 55% at 85% 0%, rgba(63, 120, 110, 0.10), transparent 60%), radial-gradient(ellipse 50% 40% at 0% 20%, rgba(193, 128, 63, 0.06), transparent 60%)",
        "grid-lines":
          "linear-gradient(to right, rgba(20, 24, 22, 0.045) 1px, transparent 1px), linear-gradient(to bottom, rgba(20, 24, 22, 0.045) 1px, transparent 1px)",
        "cta-gradient": "linear-gradient(150deg, #132623 0%, #1b423c 55%, #2c6359 100%)",
      },
      backgroundSize: {
        grid: "56px 56px",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 0.7, 0.18, 1)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: "0", transform: "translateY(14px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.7s cubic-bezier(0.22, 0.7, 0.18, 1) both",
        float: "float 6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
