import { FEATURES_SHIPPED, FEATURES_SOON, FEATURES_WONT } from "@/content/feature-map";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";
import { IconCheck } from "./icons";

function List({
  items,
  icon,
  tone,
}: {
  items: string[];
  icon: "check" | "clock" | "stop";
  tone: "default" | "muted" | "warn";
}) {
  const iconClass =
    tone === "warn"
      ? "bg-clay-100 text-clay-700"
      : tone === "muted"
        ? "bg-surface-muted text-ink-subtle"
        : "bg-brand-100 text-brand-800";

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item} className="flex gap-3 text-body text-ink-muted">
          <span
            className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${iconClass}`}
            aria-hidden
          >
            {icon === "check" ? (
              <IconCheck className="h-3 w-3" />
            ) : icon === "clock" ? (
              <span className="text-caption font-bold">→</span>
            ) : (
              <span className="text-caption font-bold">—</span>
            )}
          </span>
          <span className={tone === "default" ? "text-ink" : undefined}>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function FeatureMapSection() {
  return (
    <section className="section-y border-y border-line bg-surface">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Честная карта"
            title="Что уже есть, что в планах и чего не будет"
            description="Без маркетингового тумана: как в боте, раздел «Функции». Обновляем, когда что-то меняется."
          />
        </Reveal>
        <div className="mt-14 grid gap-6 lg:mt-20 lg:grid-cols-3">
          <Reveal>
            <div className="card h-full p-8">
              <p className="eyebrow text-brand-700">Уже работает</p>
              <div className="mt-6">
                <List items={FEATURES_SHIPPED} icon="check" tone="default" />
              </div>
            </div>
          </Reveal>
          <Reveal delay={80}>
            <div className="card h-full p-8">
              <p className="eyebrow">Скоро</p>
              <div className="mt-6">
                <List items={FEATURES_SOON} icon="clock" tone="muted" />
              </div>
            </div>
          </Reveal>
          <Reveal delay={160}>
            <div className="card h-full border-clay-200/60 bg-clay-50/30 p-8">
              <p className="eyebrow text-clay-700">Не делаем</p>
              <div className="mt-6">
                <List items={FEATURES_WONT} icon="stop" tone="warn" />
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
