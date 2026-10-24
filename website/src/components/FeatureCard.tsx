import type { ReactNode } from "react";

export function FeatureCard({
  icon,
  title,
  children,
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="card-hover group flex h-full flex-col p-7 sm:p-8">
      <div className="icon-tile group-hover:bg-brand-700 group-hover:text-white group-hover:ring-brand-700">
        {icon}
      </div>
      <h3 className="mt-6 text-title">{title}</h3>
      <p className="mt-3 flex-1 text-body text-ink-muted">{children}</p>
    </div>
  );
}
