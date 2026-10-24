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
    <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6">
      <header>
        <h1 className="font-display text-display text-ink">{title}</h1>
        <p className="mt-2 text-body-lg text-ink-muted">{subtitle}</p>
        <p className="mt-4 text-caption text-ink-subtle">Оператор: {LEGAL_OPERATOR}</p>
        <p className="text-caption text-ink-subtle">Сервис: «{BRAND}»</p>
      </header>
      <div className="mt-10 space-y-8">
        {sections.map((section) => (
          <section key={section.title}>
            <h2 className="font-display text-title text-ink">{section.title}</h2>
            <div className="mt-3 space-y-3 text-body leading-relaxed text-ink-muted">
              {section.paragraphs.map((p) => (
                <p key={p.slice(0, 40)}>{p}</p>
              ))}
            </div>
          </section>
        ))}
      </div>
      <p className="mt-12 text-caption text-ink-subtle">
        Черновик для B2B-сервиса. Уточните реквизиты оператора перед публикацией. Актуальная
        версия также доступна в Telegram-боте.
      </p>
    </article>
  );
}
