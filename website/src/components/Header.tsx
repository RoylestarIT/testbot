"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { NAV } from "@/content/constants";
import { Logo } from "./Logo";
import { TelegramButton } from "./TelegramButton";

export function Header() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-white/85 shadow-sm backdrop-blur-xl">
      <div className="container-page flex items-center justify-between gap-4 py-3.5">
        <Link
          href="/"
          className="rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600"
        >
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Основное">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
                  active
                    ? "bg-brand-50 text-brand-700"
                    : "text-ink-muted hover:bg-surface-muted hover:text-ink"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <TelegramButton
            variant="primary"
            className="hidden !rounded-full !py-2.5 !px-5 sm:inline-flex"
          >
            Открыть в Telegram
          </TelegramButton>
          <button
            type="button"
            className="rounded-xl p-2.5 text-ink-muted ring-1 ring-line md:hidden"
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
          className="border-t border-line bg-surface px-4 py-4 md:hidden"
        >
          <nav className="flex flex-col gap-1" aria-label="Мобильное">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="rounded-lg px-3 py-2.5 text-base font-medium text-ink-muted hover:bg-surface-muted hover:text-ink"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <TelegramButton variant="primary" className="mt-3 w-full !rounded-full">
              Открыть в Telegram
            </TelegramButton>
          </nav>
        </div>
      )}
    </header>
  );
}
