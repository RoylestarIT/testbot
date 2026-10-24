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
  const alignClass = align === "center" ? "mx-auto text-center" : "text-left";
  return (
    <div className={`max-w-2xl ${alignClass}`}>
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h2 className={`${eyebrow ? "mt-4" : ""} text-headline sm:text-display`}>{title}</h2>
      {description && (
        <p className={`prose-muted mt-5 ${align === "center" ? "mx-auto" : ""} max-w-prose`}>
          {description}
        </p>
      )}
    </div>
  );
}
