export function SectionHeading({
  eyebrow,
  title,
  description,
  align = "center",
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: "center" | "left";
}) {
  const alignClass = align === "center" ? "text-center mx-auto" : "text-left";
  return (
    <div className={`max-w-2xl ${alignClass}`}>
      {eyebrow && (
        <p className="text-xs font-bold uppercase tracking-widest text-brand-600">
          {eyebrow}
        </p>
      )}
      <h2 className="mt-2 text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
        {title}
      </h2>
      {description && (
        <p className="mt-4 text-pretty text-lg leading-relaxed text-slate-600">
          {description}
        </p>
      )}
    </div>
  );
}
