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
        highlight ? "ring-2 ring-brand-500/20" : ""
      }`}
    >
      <div
        className={`flex h-11 w-11 items-center justify-center rounded-xl ${
          highlight
            ? "bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-md"
            : "bg-brand-50 text-brand-700"
        }`}
      >
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{children}</p>
    </li>
  );
}
