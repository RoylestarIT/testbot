import { BRAND } from "@/content/constants";

export function Logo({
  compact = false,
  inverted = false,
}: {
  compact?: boolean;
  inverted?: boolean;
}) {
  return (
    <span className="flex items-center gap-2.5">
      <span
        className="relative flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-br from-brand-600 to-telegram shadow-md"
        aria-hidden
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5 text-white" fill="none">
          <path
            d="M4 14v-2M8 16V8M12 14V10M16 16V6M20 12v0"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </span>
      {!compact && (
        <span
          className={`text-base font-semibold tracking-tight ${
            inverted ? "text-white" : "text-slate-900"
          }`}
        >
          {BRAND}
        </span>
      )}
    </span>
  );
}
