"use client";

import { useCallback, useEffect, useState } from "react";
import { IconArrowUp } from "./icons";

const SHOW_AFTER_PX = 480;

export function BackToTopButton() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setVisible(window.scrollY > SHOW_AFTER_PX);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const scrollToTop = useCallback(() => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  }, []);

  return (
    <button
      type="button"
      onClick={scrollToTop}
      aria-label="Наверх"
      title="Наверх"
      className={`fixed right-4 z-50 flex h-12 w-12 items-center justify-center rounded-full border border-line-strong bg-white/95 text-brand-800 shadow-card backdrop-blur-md transition-all duration-300 ease-smooth hover:-translate-y-0.5 hover:border-brand-300 hover:bg-white hover:shadow-button-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 sm:right-6 sm:h-[3.25rem] sm:w-[3.25rem] ${
        visible
          ? "pointer-events-auto translate-y-0 opacity-100"
          : "pointer-events-none translate-y-3 opacity-0"
      } bottom-[calc(5.75rem+env(safe-area-inset-bottom))] sm:bottom-8`}
    >
      <IconArrowUp className="h-5 w-5" />
    </button>
  );
}
