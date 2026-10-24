import type { LegalSection } from "@/content/legal";
import { BRAND, LEGAL_OPERATOR } from "@/content/constants";

export function LegalDocument({
  title,
  subtitle,
  sections,
}: {
  title: string;
  subtitle: string;
  sections: LegalSection[];
}) {
  return (
    <div className="container-page py-16 sm:py-20 lg:py-24">
      <header className="max-w-3xl animate-fade-up">
        <p className="eyebrow">Документы</p>
        <h1 className="mt-4 text-display sm:text-display-lg">{title}</h1>
        <p className="mt-5 text-body-lg text-ink-muted">{subtitle}</p>
        <dl className="mt-8 grid gap-1 text-small text-ink-subtle">
          <div>
            <dt className="inline">Оператор: </dt>
            <dd className="inline text-ink-muted">{LEGAL_OPERATOR}</dd>
          </div>
          <div>
            <dt className="inline">Сервис: </dt>
            <dd className="inline text-ink-muted">«{BRAND}»</dd>
          </div>
        </dl>
      </header>

      <div className="mt-16 grid gap-12 border-t border-line pt-12 lg:grid-cols-[14rem_1fr] lg:gap-20">
        <nav aria-label="Содержание" className="hidden lg:sticky lg:top-28 lg:block lg:self-start">
          <p className="text-caption font-semibold uppercase tracking-[0.14em] text-ink-subtle">
            Содержание
          </p>
          <ol className="mt-4 space-y-2.5 text-small">
            {sections.map((s, i) => (
              <li key={s.title}>
                <a
                  href={`#section-${i + 1}`}
                  className="text-ink-muted transition-colors hover:text-brand-700"
                >
                  {s.title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <article className="max-w-prose">
          {sections.map((section, i) => (
            <section
              key={section.title}
              id={`section-${i + 1}`}
              className="scroll-mt-28 border-b border-line pb-10 pt-2 last:border-0 [&+&]:pt-10"
            >
              <h2 className="text-title">{section.title}</h2>
              <div className="mt-4 space-y-4 text-body text-ink-muted">
                {section.paragraphs.map((p) => (
                  <p key={p.slice(0, 40)}>{p}</p>
                ))}
              </div>
            </section>
          ))}
          <p className="mt-10 rounded-2xl bg-surface-muted p-5 text-small text-ink-subtle">
            Черновик для B2B-сервиса. Реквизиты оператора уточняются перед публикацией.
            Актуальная версия также доступна в Telegram-боте.
          </p>
        </article>
      </div>
    </div>
  );
}
