import { BRAND } from "@/content/constants";

export function Logo({
  compact = false,
  inverted = false,
}: {
  compact?: boolean;
  inverted?: boolean;
}) {
  return (
    <span className="group flex items-center gap-2.5">
      <span
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-transform duration-300 ease-smooth group-hover:rotate-[-4deg] ${
          inverted ? "bg-white text-brand-800" : "bg-brand-700 text-white"
        }`}
        aria-hidden
      >
        <svg viewBox="0 0 24 24" className="h-[1.125rem] w-[1.125rem]" fill="none">
          <path
            d="M4 13v-2M8 16V8M12 18V6M16 15V9M20 13v-2"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </span>
      {!compact && (
        <span
          className={`font-display text-[1.0625rem] font-semibold tracking-[-0.02em] ${
            inverted ? "text-white" : "text-ink"
          }`}
        >
          {BRAND}
        </span>
      )}
    </span>
  );
}
