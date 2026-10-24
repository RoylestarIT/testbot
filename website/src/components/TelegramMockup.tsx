/** Стилизованный mockup чата Telegram без персональных данных. */

export function TelegramMockup({ variant = "review" }: { variant?: "review" | "pricing" }) {
  return (
    <div className="relative mx-auto w-full max-w-[340px] lg:max-w-md">
      <div
        className="absolute -inset-4 rounded-[2rem] bg-gradient-to-br from-brand-400/30 to-telegram/20 blur-2xl"
        aria-hidden
      />
      <div
        className="relative overflow-hidden rounded-[1.75rem] border border-black/20 bg-[#17212b] shadow-mockup ring-1 ring-white/10"
        aria-hidden
      >
        <div className="flex items-center gap-3 border-b border-white/10 bg-[#1e2c3a] px-4 py-3.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-brand-500 to-telegram text-xs font-bold text-white">
            ГБ
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Голос бренда</p>
            <p className="text-xs text-[#6bc99a]">● онлайн</p>
          </div>
        </div>
        <div className="space-y-3 px-3 py-5 text-[13px] leading-snug">
          {variant === "review" ? (
            <>
              <Bubble align="left" muted>
                <span className="text-amber-300">★★★★★</span> Новый отзыв · WB
                <br />
                <span className="text-white/75">«Быстрая доставка, размер подошёл»</span>
              </Bubble>
              <Bubble align="left" accent>
                Вариант 1: Спасибо за отзыв! Рады, что размер подошёл…
              </Bubble>
              <Bubble align="left">
                Вариант 2: Благодарим! Если понадобится другой размер — напишите…
              </Bubble>
              <div className="flex flex-wrap gap-2 px-0.5 pt-1">
                {["✏️ Править", "📤 Publish", "📋 Копия"].map((label) => (
                  <span
                    key={label}
                    className="rounded-lg bg-white/10 px-2.5 py-1.5 text-xs font-medium text-sky-100 ring-1 ring-white/10"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <>
              <Bubble align="left" muted>
                📊 Сравнение тарифов · Lite vs PRO
              </Bubble>
              <Bubble align="left" accent>
                Lite: ∞ генераций · PRO: publish + авто 4–5★
              </Bubble>
              <div className="flex flex-wrap gap-2 px-0.5 pt-1">
                {["⭐ Stars", "💳 Карта", "🪙 USDT"].map((label) => (
                  <span
                    key={label}
                    className="rounded-lg bg-white/10 px-2.5 py-1.5 text-xs font-medium text-sky-100"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Bubble({
  children,
  align,
  muted,
  accent,
}: {
  children: React.ReactNode;
  align: "left" | "right";
  muted?: boolean;
  accent?: boolean;
}) {
  let bg = "bg-[#2b5278]/95 text-white";
  if (muted) bg = "bg-[#243447] text-white/85 ring-1 ring-white/5";
  if (accent) bg = "bg-[#2b5278] text-white ring-1 ring-brand-400/30";

  return (
    <div className={`flex ${align === "right" ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[92%] rounded-2xl rounded-tl-md px-3.5 py-2.5 ${bg}`}>
        {children}
      </div>
    </div>
  );
}
