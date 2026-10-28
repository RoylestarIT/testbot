"use client";

import { useId, useState } from "react";
import type { FaqItem } from "@/content/faq";

export function FAQAccordion({ items }: { items: FaqItem[] }) {
  const baseId = useId();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="divide-y divide-line border-y border-line">
      {items.map((item, index) => {
        const isOpen = openIndex === index;
        const panelId = `${baseId}-panel-${index}`;
        const buttonId = `${baseId}-btn-${index}`;
        return (
          <div key={item.question} id={item.id} className={item.id ? "scroll-mt-28" : undefined}>
            <h3>
              <button
                id={buttonId}
                type="button"
                className="group flex w-full items-center justify-between gap-6 py-6 text-left font-display text-title font-medium text-ink transition-colors hover:text-brand-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpenIndex(isOpen ? null : index)}
              >
                <span>{item.question}</span>
                <span
                  className={`relative flex h-9 w-9 shrink-0 items-center justify-center rounded-full ring-1 transition-all duration-300 ease-smooth ${
                    isOpen
                      ? "rotate-45 bg-brand-700 text-white ring-brand-700"
                      : "text-ink-muted ring-line-strong group-hover:ring-brand-300"
                  }`}
                  aria-hidden
                >
                  <span className="absolute h-px w-3.5 bg-current" />
                  <span className="absolute h-3.5 w-px bg-current" />
                </span>
              </button>
            </h3>
            <div
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              inert={!isOpen}
              className={`grid transition-[grid-template-rows,opacity] duration-300 ease-smooth ${
                isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
              }`}
            >
              <div className="overflow-hidden">
                <p className="max-w-prose pb-7 pr-14 text-body text-ink-muted">{item.answer}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
