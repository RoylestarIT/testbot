"use client";

import { useId, useState } from "react";
import type { FaqItem } from "@/content/faq";

export function FAQAccordion({ items }: { items: FaqItem[] }) {
  const baseId = useId();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="divide-y divide-line overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      {items.map((item, index) => {
        const isOpen = openIndex === index;
        const panelId = `${baseId}-panel-${index}`;
        const buttonId = `${baseId}-btn-${index}`;
        return (
          <div key={item.question} className="bg-white">
            <h3>
              <button
                id={buttonId}
                type="button"
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left text-base font-semibold text-slate-900 transition hover:bg-slate-50/80 focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-brand-600 sm:px-6 sm:py-5"
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => setOpenIndex(isOpen ? null : index)}
              >
                <span className="text-pretty">{item.question}</span>
                <span
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-normal transition ${
                    isOpen ? "bg-brand-100 text-brand-700" : "bg-slate-100 text-slate-500"
                  }`}
                  aria-hidden
                >
                  {isOpen ? "−" : "+"}
                </span>
              </button>
            </h3>
            <div
              id={panelId}
              role="region"
              aria-labelledby={buttonId}
              hidden={!isOpen}
              className="border-t border-slate-50 px-5 pb-5 pt-1 text-sm leading-relaxed text-slate-600 sm:px-6 sm:pb-6"
            >
              {item.answer}
            </div>
          </div>
        );
      })}
    </div>
  );
}
