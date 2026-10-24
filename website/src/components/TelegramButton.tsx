import Link from "next/link";
import { BOT_URL, BOT_URL_SITE } from "@/content/constants";

type Props = {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "ghost";
  className?: string;
  trackSite?: boolean;
};

const base =
  "inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600";

const variants = {
  primary: `${base} bg-blue-600 text-white hover:bg-blue-700 shadow-sm`,
  secondary: `${base} bg-white text-slate-900 ring-1 ring-slate-200 hover:bg-slate-50`,
  ghost: `${base} text-blue-700 hover:bg-blue-50`,
};

export function TelegramButton({
  children,
  variant = "primary",
  className = "",
  trackSite = false,
}: Props) {
  const href = trackSite ? BOT_URL_SITE : BOT_URL;
  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`${variants[variant]} ${className}`}
    >
      <TelegramIcon />
      {children}
    </Link>
  );
}

function TelegramIcon() {
  return (
    <svg
      aria-hidden
      className="h-5 w-5 shrink-0"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.88-1.08.2-1.6l15.57-6.01c.73-.33 1.43.18 1.15 1.3l-2.65 12.42c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z" />
    </svg>
  );
}
