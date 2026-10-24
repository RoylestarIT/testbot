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
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h2 className="mt-3 text-balance font-display text-display text-ink sm:text-[2.625rem]">
        {title}
      </h2>
      {description && (
        <p className="prose-muted mt-4 text-pretty">{description}</p>
      )}
    </div>
  );
}
