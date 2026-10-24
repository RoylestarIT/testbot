/** Стилизованный mockup чата Telegram без персональных данных. */

export function TelegramMockup({ variant = "review" }: { variant?: "review" | "pricing" }) {
  return (
    <div
      className="mx-auto w-full max-w-sm overflow-hidden rounded-2xl border border-slate-200 bg-[#17212b] shadow-xl"
      aria-hidden
    >
      <div className="flex items-center gap-3 border-b border-white/10 px-4 py-3">
        <div className="h-8 w-8 rounded-full bg-blue-500/80" />
        <div>
          <p className="text-sm font-medium text-white">Голос бренда</p>
          <p className="text-xs text-slate-400">bot</p>
        </div>
      </div>
      <div className="space-y-3 px-3 py-4 text-sm">
        {variant === "review" ? (
          <>
            <Bubble align="left" muted>
              ⭐⭐⭐⭐⭐ Новый отзыв · WB · арт. ••••1234
              <br />
              «Быстрая доставка, размер подошёл»
            </Bubble>
            <Bubble align="left">
              Вариант 1: Спасибо за отзыв! Рады, что размер подошёл…
            </Bubble>
            <Bubble align="left">
              Вариант 2: Благодарим! Если понадобится другой размер — напишите…
            </Bubble>
            <div className="flex flex-wrap gap-2 pl-1">
              {["✏️ Править", "📤 Publish", "📋 Копия"].map((label) => (
                <span
                  key={label}
                  className="rounded-lg bg-white/10 px-2 py-1 text-xs text-sky-200"
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
            <Bubble align="left">
              Lite: ∞ генераций, несколько кабинетов
              <br />
              PRO: publish + авто 4–5★
            </Bubble>
            <div className="flex flex-wrap gap-2 pl-1">
              {["⭐ Stars", "💳 Карта", "🪙 USDT"].map((label) => (
                <span
                  key={label}
                  className="rounded-lg bg-white/10 px-2 py-1 text-xs text-sky-200"
                >
                  {label}
                </span>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Bubble({
  children,
  align,
  muted,
}: {
  children: React.ReactNode;
  align: "left" | "right";
  muted?: boolean;
}) {
  return (
    <div className={`flex ${align === "right" ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[90%] rounded-2xl px-3 py-2 leading-snug ${
          muted
            ? "bg-[#2b5278] text-slate-200"
            : "bg-[#2b5278]/90 text-white"
        }`}
      >
        {children}
      </div>
    </div>
  );
}
