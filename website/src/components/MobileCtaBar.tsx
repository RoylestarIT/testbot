"use client";

import { useEffect, useState } from "react";
import { TelegramButton } from "./TelegramButton";

export function MobileCtaBar() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      const nearBottom =
        window.innerHeight + window.scrollY > document.documentElement.scrollHeight - 480;
      setVisible(window.scrollY > 640 && !nearBottom);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div
      className={`fixed inset-x-0 bottom-0 z-40 border-t border-line bg-[rgba(250,250,248,0.92)] px-4 pb-[calc(0.75rem+env(safe-area-inset-bottom))] pt-3 backdrop-blur-xl transition-transform duration-300 ease-smooth sm:hidden ${
        visible ? "translate-y-0" : "translate-y-full"
      }`}
      aria-hidden={!visible}
      inert={!visible}
    >
      <div className="flex items-center gap-3">
        <p className="flex-1 text-caption leading-snug text-ink-muted">
          Бесплатно, без карты
          <br />
          <span className="font-medium text-ink">5 ответов в день</span>
        </p>
        <TelegramButton trackSite>Начать бесплатно</TelegramButton>
      </div>
    </div>
  );
}
