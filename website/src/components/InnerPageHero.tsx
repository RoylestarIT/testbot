export function InnerPageHero({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <section className="relative overflow-hidden border-b border-line bg-hero-mesh bg-surface-muted/50">
      <div className="container-page py-14 sm:py-16">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-balance font-display text-display text-ink sm:text-display-lg">
            {title}
          </h1>
          {description && (
            <p className="prose-muted mx-auto mt-5 max-w-2xl text-pretty">{description}</p>
          )}
        </div>
      </div>
    </section>
  );
}
