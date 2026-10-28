import { MARKET_COMPARE_ROWS } from "@/content/market-compare";

export function MarketCompareTable() {
  return (
    <div className="overflow-hidden rounded-3xl border border-line">
      <div className="grid grid-cols-[1fr_1fr_1fr] bg-surface-muted text-small font-medium text-ink-subtle">
        <div className="px-5 py-4 sm:px-7" />
        <div className="bg-brand-50 px-5 py-4 font-display font-semibold text-brand-800 sm:px-7">
          Голос бренда
        </div>
        <div className="px-5 py-4 sm:px-7">Обычно у других</div>
      </div>
      {MARKET_COMPARE_ROWS.map((row) => (
        <div
          key={row.label}
          className="grid grid-cols-[1fr_1fr_1fr] border-t border-line text-small transition-colors hover:bg-surface-elevated sm:text-body"
        >
          <div className="px-5 py-4 font-medium text-ink sm:px-7">{row.label}</div>
          <div className="bg-brand-50/40 px-5 py-4 text-ink sm:px-7">{row.us}</div>
          <div className="px-5 py-4 text-ink-subtle sm:px-7">{row.market}</div>
        </div>
      ))}
    </div>
  );
}
