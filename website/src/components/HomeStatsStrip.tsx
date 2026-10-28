import { Reveal } from "@/components/Reveal";

type StatItem =
  | { kind: "static"; value: string; label: string; accent?: boolean }
  | { kind: "today"; label: string };

const items: StatItem[] = [
  { kind: "static", value: "3", label: "варианта ответа на каждый отзыв" },
  { kind: "static", value: "2", label: "площадки в одном чате — WB и Ozon" },
  { kind: "today", label: "человек воспользовались ботом сегодня" },
  { kind: "static", value: "0", label: "автоответов на отзывы 1–3★", accent: true },
];

function StatValue({ item }: { item: StatItem }) {
  if (item.kind === "today") {
    return (
      <span
        id="stat-today"
        className="font-display text-display font-semibold tabular-nums tracking-tight text-brand-700 sm:text-display-lg"
      >
        127
      </span>
    );
  }

  return (
    <span
      className={`font-display text-display font-semibold tabular-nums tracking-tight sm:text-display-lg ${
        item.accent ? "text-brand-700" : "text-ink"
      }`}
    >
      {item.value}
    </span>
  );
}

export function HomeStatsStrip() {
  return (
    <section className="border-y border-line bg-line" aria-label="Ключевые цифры">
      <div className="container-page">
        <ul className="grid grid-cols-2 gap-px lg:grid-cols-4">
          {items.map((item, i) => (
            <Reveal key={item.label} delay={i * 60} as="li" className="bg-surface">
              <div className="flex h-full flex-col items-center justify-center px-4 py-10 text-center sm:px-6 sm:py-12">
                <StatValue item={item} />
                <p className="mt-3 max-w-[11rem] text-balance text-small leading-snug text-ink-muted sm:max-w-[13rem]">
                  {item.label}
                </p>
                {item.kind === "today" ? (
                  <p className="mt-2 text-caption text-ink-subtle">
                    за месяц —{" "}
                    <span
                      id="stat-month"
                      className="font-display font-semibold tabular-nums text-brand-700"
                    >
                      3&nbsp;841
                    </span>
                  </p>
                ) : null}
              </div>
            </Reveal>
          ))}
        </ul>
      </div>
    </section>
  );
}
