import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";
import { MarketCompareTable } from "./MarketCompareTable";

export function MarketCompareSection() {
  return (
    <section className="section-y bg-surface-muted">
      <div className="container-page max-w-4xl">
        <Reveal>
          <SectionHeading
            eyebrow="Сравнение"
            title="Мы и «как обычно на рынке»"
            description="Без имён конкурентов — просто то, что селлеры замечают, когда сравнивают сервисы для отзывов."
          />
        </Reveal>
        <Reveal delay={100}>
          <div className="mt-14">
            <MarketCompareTable />
          </div>
        </Reveal>
      </div>
    </section>
  );
}
