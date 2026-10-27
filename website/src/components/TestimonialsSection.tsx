import { TESTIMONIALS, type Testimonial } from "@/content/testimonials";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

const avatarTones = [
  "bg-brand-100 text-brand-800",
  "bg-clay-100 text-clay-600",
  "bg-[#e4ecf5] text-[#2d5b8a]",
  "bg-[#efe7f3] text-[#6b4483]",
];

function Card({ t, index }: { t: Testimonial; index: number }) {
  return (
    <figure className="card-hover flex h-full flex-col p-7">
      <div className="flex items-center justify-between gap-3">
        <div className="flex gap-0.5 text-clay-500" aria-label="Оценка 5 из 5">
          {Array.from({ length: 5 }).map((_, j) => (
            <svg key={j} viewBox="0 0 20 20" className="h-4 w-4" fill="currentColor" aria-hidden>
              <path d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.5 7.7l5.9-.9z" />
            </svg>
          ))}
        </div>
        <span className="rounded-full bg-surface-muted px-2.5 py-1 text-caption font-medium text-ink-muted">
          {t.market}
        </span>
      </div>
      <blockquote className="mt-5 flex-1 text-body leading-relaxed text-ink">«{t.quote}»</blockquote>
      <figcaption className="mt-6 flex items-center gap-3 border-t border-line pt-5">
        <span
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full font-display text-small font-semibold ${
            avatarTones[index % avatarTones.length]
          }`}
          aria-hidden
        >
          {t.name.slice(0, 1)}
        </span>
        <span className="min-w-0">
          <span className="block font-display text-body font-semibold text-ink">{t.name}</span>
          <span className="block text-small text-ink-subtle">
            {t.role} · тариф {t.plan}
          </span>
        </span>
      </figcaption>
    </figure>
  );
}

export function TestimonialsSection() {
  return (
    <section className="section-y border-y border-line bg-surface">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Отзывы"
            title="Что говорят селлеры"
            description="Магазины разного размера — от сотни отзывов в месяц до двух кабинетов на разных площадках."
          />
        </Reveal>
        <div className="mt-16 grid gap-5 md:grid-cols-2 lg:mt-20 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <Reveal key={t.name} delay={(i % 3) * 80}>
              <Card t={t} index={i} />
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
