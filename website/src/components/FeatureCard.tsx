import type { ReactNode } from "react";

export function FeatureCard({
  icon,
  title,
  children,
  highlight,
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  highlight?: boolean;
}) {
  return (
    <li
      className={`card-hover flex flex-col p-6 sm:p-7 ${
        highlight ? "ring-1 ring-brand-200/80 bg-gradient-to-b from-brand-50/40 to-white" : ""
      }`}
    >
      <div
        className={`flex h-11 w-11 items-center justify-center rounded-xl ${
          highlight
            ? "bg-brand-600 text-white shadow-sm"
            : "bg-surface-muted text-brand-700 ring-1 ring-line"
        }`}
      >
        {icon}
      </div>
      <h3 className="mt-4 font-display text-title text-ink">{title}</h3>
      <p className="mt-2.5 flex-1 text-body text-ink-muted">{children}</p>
    </li>
  );
}
