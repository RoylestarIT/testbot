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
        <h1 className="text-3xl font-bold text-slate-900">{title}</h1>
        <p className="mt-2 text-slate-600">{subtitle}</p>
        <p className="mt-4 text-sm text-slate-500">Оператор: {LEGAL_OPERATOR}</p>
        <p className="text-sm text-slate-500">Сервис: «{BRAND}»</p>
      </header>
      <div className="mt-10 space-y-8">
        {sections.map((section) => (
          <section key={section.title}>
            <h2 className="text-lg font-semibold text-slate-900">{section.title}</h2>
            <div className="mt-3 space-y-3 text-sm leading-relaxed text-slate-700">
              {section.paragraphs.map((p, i) => (
                <p key={`${section.title}-${i}`}>{p}</p>
              ))}
            </div>
          </section>
        ))}
      </div>
      <p className="mt-12 text-xs text-slate-500">
        Черновик для B2B-сервиса. Уточните реквизиты оператора перед публикацией. Актуальная
        версия также доступна в Telegram-боте.
      </p>
    </article>
  );
}
