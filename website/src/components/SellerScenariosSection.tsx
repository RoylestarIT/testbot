import { SELLER_SCENARIOS } from "@/content/seller-scenarios";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

export function SellerScenariosSection() {
  return (
    <section className="section-y border-y border-line bg-surface-muted">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Узнаёте себя?"
            title="Типичные ситуации селлеров"
            description="Это не отзывы покупателей и не «1000+ довольных клиентов» — просто сценарии, с которыми к нам чаще всего приходят."
          />
        </Reveal>
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:mt-20 lg:grid-cols-3">
          {SELLER_SCENARIOS.map((s, i) => (
            <Reveal key={s.title} delay={(i % 3) * 70}>
              <article className="card-hover flex h-full flex-col p-7">
                <span className="w-fit rounded-full bg-surface px-2.5 py-1 text-caption font-medium text-ink-muted ring-1 ring-line">
                  {s.tag}
                </span>
                <h3 className="mt-5 font-display text-title text-ink">{s.title}</h3>
                <p className="mt-3 flex-1 text-body text-ink-muted">{s.situation}</p>
                <p className="mt-5 border-t border-line pt-5 text-body text-ink">
                  <span className="font-medium text-brand-800">Как помогает бот: </span>
                  {s.outcome}
                </p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
