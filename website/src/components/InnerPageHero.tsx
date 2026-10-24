export function InnerPageHero({
  title,
  description,
  eyebrow,
}: {
  title: string;
  description?: string;
  eyebrow?: string;
}) {
  return (
    <section className="relative -mt-16 overflow-hidden pt-16 sm:-mt-[4.5rem] sm:pt-[4.5rem]">
      <div className="absolute inset-0 bg-hero-mesh" aria-hidden />
      <div className="mask-fade-b absolute inset-0 bg-grid-lines bg-grid opacity-60" aria-hidden />
      <div className="container-page relative pb-14 pt-16 sm:pb-16 sm:pt-20">
        <div className="mx-auto max-w-3xl animate-fade-up text-center">
          {eyebrow && <p className="eyebrow">{eyebrow}</p>}
          <h1 className={`${eyebrow ? "mt-4" : ""} text-display sm:text-display-lg`}>{title}</h1>
          {description && (
            <p className="prose-muted mx-auto mt-6 max-w-prose">{description}</p>
          )}
        </div>
      </div>
    </section>
  );
}
