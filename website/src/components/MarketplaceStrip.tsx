const items = [
  { label: "Wildberries", dot: "bg-[#a13a7a]" },
  { label: "Ozon", dot: "bg-[#2d6fd2]" },
  { label: "Telegram", dot: "bg-telegram" },
];

export function MarketplaceStrip() {
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-small text-ink-subtle">
      <span>Работает с</span>
      <ul className="flex flex-wrap items-center gap-x-5 gap-y-2" aria-label="Площадки">
        {items.map((item) => (
          <li key={item.label} className="inline-flex items-center gap-2 font-medium text-ink-muted">
            <span className={`h-2 w-2 rounded-full ${item.dot}`} aria-hidden />
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
