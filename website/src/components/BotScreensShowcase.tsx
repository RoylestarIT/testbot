"use client";

import { useState } from "react";
import { BOT_SCREENSHOTS } from "@/content/bot-screenshots";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

export function BotScreensShowcase() {
  const [active, setActive] = useState(0);
  const shot = BOT_SCREENSHOTS[active];

  return (
    <section className="section-y bg-surface-muted">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Как это выглядит"
            title="Так выглядит бот в Telegram"
            description="Настоящие экраны @FeedBackReview_bot, а не картинки для красоты. Всё просто и понятно с первого раза."
          />
        </Reveal>

        <div className="mt-14 grid gap-10 lg:mt-20 lg:grid-cols-[minmax(0,1fr)_minmax(280px,360px)] lg:items-start lg:gap-14">
          <Reveal className="lg:sticky lg:top-28">
            <div className="relative mx-auto max-w-md">
              <div
                className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-brand-200/40 to-clay-100/30 blur-2xl"
                aria-hidden
              />
              <div className="relative overflow-hidden rounded-[2rem] border border-line bg-[#0e1621] p-2 shadow-mockup ring-1 ring-black/5">
                {/* eslint-disable-next-line @next/next/no-img-element -- static export */}
                <img
                  key={shot.id}
                  src={shot.src}
                  alt={shot.alt}
                  width={900}
                  height={1600}
                  loading={active === 0 ? "eager" : "lazy"}
                  className="w-full rounded-[1.35rem] object-cover object-[center_top] transition-opacity duration-300"
                />
              </div>
              <p className="mt-5 text-center text-small text-ink-muted">{shot.caption}</p>
            </div>
          </Reveal>

          <Reveal delay={100}>
            <ul className="flex flex-col gap-2">
              {BOT_SCREENSHOTS.map((item, i) => {
                const selected = i === active;
                return (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => setActive(i)}
                      className={`flex w-full items-center gap-4 rounded-2xl border px-4 py-3.5 text-left transition duration-200 ease-smooth ${
                        selected
                          ? "border-brand-300 bg-surface shadow-card"
                          : "border-transparent bg-surface/60 hover:border-line hover:bg-surface"
                      }`}
                    >
                      <span
                        className={`flex h-14 w-10 shrink-0 overflow-hidden rounded-lg border ${
                          selected ? "border-brand-200" : "border-line"
                        }`}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={item.src}
                          alt=""
                          loading="lazy"
                          className="h-full w-full object-cover object-[center_top]"
                        />
                      </span>
                      <span>
                        <span className="block font-display text-body font-semibold text-ink">
                          {item.title}
                        </span>
                        <span className="mt-0.5 block text-caption text-ink-subtle line-clamp-2">
                          {item.caption}
                        </span>
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
