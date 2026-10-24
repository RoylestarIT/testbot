"use client";

import Link from "next/link";
import { useState } from "react";
import { BRAND, NAV } from "@/content/constants";
import { TelegramButton } from "./TelegramButton";

export function Header() {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
        >
          <span
            className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 text-sm text-white"
            aria-hidden
          >
            ГБ
          </span>
          <span className="hidden sm:inline">{BRAND}</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex" aria-label="Основное">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-slate-600 hover:text-slate-900"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <TelegramButton variant="primary" className="hidden sm:inline-flex py-2.5 px-4 text-sm">
            Открыть в Telegram
          </TelegramButton>
          <button
            type="button"
            className="rounded-lg p-2 text-slate-700 ring-1 ring-slate-200 md:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? "Закрыть меню" : "Открыть меню"}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {open && (
        <div
          id="mobile-nav"
          className="border-t border-slate-200 bg-white px-4 py-4 md:hidden"
        >
          <nav className="flex flex-col gap-3" aria-label="Мобильное">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-base text-slate-700"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <TelegramButton variant="primary" className="mt-2 w-full">
              Открыть в Telegram
            </TelegramButton>
          </nav>
        </div>
      )}
    </header>
  );
}
