"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { NAV } from "@/content/constants";
import { Logo } from "./Logo";
import { TelegramButton } from "./TelegramButton";

export function Header() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`sticky top-0 z-50 border-b transition-colors duration-300 ease-smooth ${
        scrolled || open
          ? "border-line bg-[rgba(250,250,248,0.82)] backdrop-blur-xl"
          : "border-transparent bg-transparent"
      }`}
    >
      <div className="container-page flex h-16 items-center justify-between gap-6 sm:h-[4.5rem]">
        <Link
          href="/"
          className="rounded-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-brand-500"
        >
          <Logo />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Основное">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative rounded-full px-3.5 py-2 text-small font-medium transition-colors duration-200 ${
                  active ? "text-ink" : "text-ink-muted hover:text-ink"
                }`}
              >
                {item.label}
                <span
                  className={`absolute inset-x-3.5 -bottom-0.5 h-px origin-left bg-brand-600 transition-transform duration-300 ease-smooth ${
                    active ? "scale-x-100" : "scale-x-0"
                  }`}
                  aria-hidden
                />
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <TelegramButton trackSite className="hidden sm:inline-flex">
            Попробовать бесплатно
          </TelegramButton>
          <button
            type="button"
            className="flex h-11 w-11 items-center justify-center rounded-full text-ink ring-1 ring-line transition hover:bg-surface-muted lg:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            aria-label={open ? "Закрыть меню" : "Открыть меню"}
            onClick={() => setOpen((v) => !v)}
          >
            <span className="relative block h-3 w-4" aria-hidden>
              <span
                className={`absolute left-0 top-0 h-px w-4 bg-current transition-transform duration-300 ${
                  open ? "translate-y-1.5 rotate-45" : ""
                }`}
              />
              <span
                className={`absolute left-0 top-1.5 h-px w-4 bg-current transition-opacity duration-200 ${
                  open ? "opacity-0" : ""
                }`}
              />
              <span
                className={`absolute left-0 top-3 h-px w-4 bg-current transition-transform duration-300 ${
                  open ? "-translate-y-1.5 -rotate-45" : ""
                }`}
              />
            </span>
          </button>
        </div>
      </div>

      {open && (
        <div id="mobile-nav" className="border-t border-line px-5 pb-6 pt-3 lg:hidden">
          <nav className="flex flex-col" aria-label="Мобильное">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="border-b border-line py-3.5 text-body font-medium text-ink last:border-0"
                onClick={() => setOpen(false)}
              >
                {item.label}
              </Link>
            ))}
            <TelegramButton trackSite size="lg" className="mt-4 w-full">
              Попробовать бесплатно
            </TelegramButton>
          </nav>
        </div>
      )}
    </header>
  );
}
