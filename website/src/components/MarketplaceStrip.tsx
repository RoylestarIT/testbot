export function MarketplaceStrip() {
  const items = [
    { label: "Wildberries", className: "bg-[#fdf2f8] text-[#9d174d] border-[#f9d8e8]" },
    { label: "Ozon", className: "bg-telegram-soft text-[#1e6a8a] border-[#cce9f5]" },
    { label: "Telegram", className: "bg-[#eef6fc] text-[#2563a8] border-[#d6e9f7]" },
    {
      label: "ИИ + ваш контроль",
      className: "bg-brand-50 text-brand-800 border-brand-100",
    },
  ];

  return (
    <ul className="flex flex-wrap gap-2" aria-label="Площадки и формат">
      {items.map((item) => (
        <li
          key={item.label}
          className={`rounded-full border px-3.5 py-1 text-caption font-semibold ${item.className}`}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
}
