import { TESTIMONIALS } from "@/content/testimonials";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

export function TestimonialsSection() {
  return (
    <section className="section-y border-y border-line bg-surface">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Отзывы селлеров"
            title="Как это работает в реальной рутине"
            description="Типичные сценарии — без обещаний «100% автопилота» и без выдуманных брендов."
          />
        </Reveal>
        <div className="mt-16 grid gap-6 lg:mt-20 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <Reveal key={t.name} delay={i * 80}>
              <figure className="card-hover flex h-full flex-col p-8">
                <div className="flex gap-0.5 text-clay-500" aria-hidden>
                  {"★★★★★".split("").map((s, j) => (
                    <span key={j} className="text-sm">
                      {s}
                    </span>
                  ))}
                </div>
                <blockquote className="mt-5 flex-1 text-body leading-relaxed text-ink">
                  «{t.quote}»
                </blockquote>
                <figcaption className="mt-8 border-t border-line pt-6">
                  <p className="font-display text-body font-semibold text-ink">{t.name}</p>
                  <p className="mt-1 text-small text-ink-muted">{t.role}</p>
                  <p className="mt-2 text-caption text-ink-subtle">{t.detail}</p>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
