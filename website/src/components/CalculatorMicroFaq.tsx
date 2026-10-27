import Link from "next/link";
import { CALCULATOR_MICRO_FAQ } from "@/content/calculator-micro-faq";

export function CalculatorMicroFaq() {
  return (
    <div className="mt-8 rounded-3xl border border-line bg-surface-muted/70 p-6 sm:p-8">
      <p className="eyebrow">Если сомневаетесь</p>
      <h4 className="mt-3 font-display text-title text-ink">Коротко о главном</h4>
      <div className="mt-6 divide-y divide-line">
        {CALCULATOR_MICRO_FAQ.map((item) => (
          <details key={item.question} className="group py-4 first:pt-0 last:pb-0">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-body font-semibold text-ink marker:content-none [&::-webkit-details-marker]:hidden">
              <span>{item.question}</span>
              <span
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface text-ink-subtle ring-1 ring-line transition duration-200 group-open:rotate-45 group-open:bg-brand-50 group-open:text-brand-700 group-open:ring-brand-200"
                aria-hidden
              >
                +
              </span>
            </summary>
            <p className="mt-3 max-w-prose text-body text-ink-muted">{item.answer}</p>
          </details>
        ))}
      </div>
      <p className="mt-6 text-caption text-ink-subtle">
        Больше ответов — в{" "}
        <Link href="/faq" className="font-medium text-brand-700 hover:underline">
          разделе FAQ
        </Link>
        .
      </p>
    </div>
  );
}
