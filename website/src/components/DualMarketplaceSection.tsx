import { Reveal } from "./Reveal";

const platforms = [
  {
    name: "Wildberries",
    dot: "bg-[#a13a7a]",
    text: "Отзывы и вопросы покупателей — в общей ленте с Ozon.",
  },
  {
    name: "Ozon",
    dot: "bg-[#2d6fd2]",
    text: "Второй сервис не нужен: один бот и один стиль ответов.",
  },
];

function PlatformCard({
  name,
  dot,
  text,
}: {
  name: string;
  dot: string;
  text: string;
}) {
  return (
    <article className="flex min-h-[9.5rem] flex-col rounded-2xl border border-white/10 bg-white/[0.06] p-6 sm:p-7">
      <p className="inline-flex items-center gap-2.5 font-display text-title font-semibold text-white">
        <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${dot}`} aria-hidden />
        {name}
      </p>
      <p className="mt-4 flex-1 text-body leading-relaxed text-brand-100">{text}</p>
    </article>
  );
}

function HubConnector() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-2 lg:px-2 lg:py-6">
      <div
        className="hidden h-px w-full max-w-[4.5rem] bg-gradient-to-r from-transparent via-white/25 to-transparent lg:block"
        aria-hidden
      />
      <div className="flex w-full items-center justify-center gap-3 lg:flex-col lg:gap-4">
        <span
          className="hidden h-px flex-1 bg-white/15 lg:block lg:h-12 lg:w-px lg:flex-none"
          aria-hidden
        />
        <div className="flex flex-col items-center gap-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 ring-1 ring-white/20">
            <svg viewBox="40 56 140 140" className="h-6 w-6 text-white" fill="currentColor" aria-hidden>
              <path d="M98 175c-3.888 0-3.227-1.468-4.568-5.17L82 132.207 170 80" />
              <path d="M98 175c3 0 4.325-1.372 6-3l16-15.558-19.958-12.035" />
              <path d="M100.04 144.41l48.36 35.729c5.519 3.045 9.501 1.468 10.876-5.123l19.685-92.763c2.015-8.08-3.08-11.746-8.36-9.349l-115.59 44.571c-7.89 3.165-7.843 7.567-1.438 9.528l29.663 9.259 68.673-43.325c3.242-1.966 6.218-.91 3.776 1.258" />
            </svg>
          </div>
          <p className="max-w-[9rem] text-center text-caption font-medium leading-snug text-brand-200">
            Один чат вместо двух кабинетов
          </p>
        </div>
        <span
          className="hidden h-px flex-1 bg-white/15 lg:block lg:h-12 lg:w-px lg:flex-none"
          aria-hidden
        />
      </div>
      <div
        className="flex w-full items-center gap-2 text-brand-300/80 lg:hidden"
        aria-hidden
      >
        <span className="h-px flex-1 bg-white/15" />
        <span className="text-caption">↓</span>
        <span className="h-px flex-1 bg-white/15" />
      </div>
    </div>
  );
}

export function DualMarketplaceSection() {
  const [wb, ozon] = platforms;

  return (
    <section className="section-y overflow-hidden bg-brand-900 text-white">
      <div className="container-page">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-caption font-semibold uppercase tracking-[0.14em] text-brand-300">
              Wildberries и Ozon
            </p>
            <h2 className="mt-4 text-headline text-white sm:text-display">Один Telegram — две площадки</h2>
            <p className="mx-auto mt-5 max-w-prose text-body-lg text-brand-100">
              Многие сервисы заточены только под WB. Мы с самого начала делаем обе площадки: отзывы,
              черновики и история — в одном месте.
            </p>
          </div>
        </Reveal>

        <Reveal delay={80}>
          <div className="relative mt-14 rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.07] to-white/[0.02] p-5 sm:mt-16 sm:p-8 lg:mt-20 lg:p-10">
            <div
              className="pointer-events-none absolute inset-0 rounded-3xl opacity-40"
              style={{
                backgroundImage:
                  "linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px)",
                backgroundSize: "24px 24px",
              }}
              aria-hidden
            />
            <div className="relative grid gap-4 lg:grid-cols-[1fr_minmax(7rem,8.5rem)_1fr] lg:items-stretch lg:gap-6">
              <PlatformCard {...wb} />
              <HubConnector />
              <PlatformCard {...ozon} />
            </div>
          </div>
        </Reveal>

        <Reveal delay={140}>
          <p className="mx-auto mt-10 max-w-2xl text-center text-small leading-relaxed text-brand-200/90 sm:mt-12">
            На Lite — до двух кабинетов, на PRO — до четырёх. Стиль общения один на все магазины или
            свой для каждого — как вам удобнее.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
