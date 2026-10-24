export function InnerPageHero({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <section className="relative overflow-hidden border-b border-slate-200/80 bg-hero-mesh">
      <div className="container-page section-y !py-12 sm:!py-16">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl lg:text-[2.5rem]">
            {title}
          </h1>
          {description && (
            <p className="mt-4 text-pretty text-lg leading-relaxed text-slate-600">
              {description}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
