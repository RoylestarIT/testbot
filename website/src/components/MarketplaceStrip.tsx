export function MarketplaceStrip() {
  const items = [
    { label: "Wildberries", color: "bg-fuchsia-50 text-fuchsia-800 border-fuchsia-100" },
    { label: "Ozon", color: "bg-sky-50 text-sky-900 border-sky-100" },
    { label: "Telegram", color: "bg-blue-50 text-blue-900 border-blue-100" },
    { label: "ИИ + ваш контроль", color: "bg-violet-50 text-violet-900 border-violet-100" },
  ];

  return (
    <ul className="flex flex-wrap gap-2" aria-label="Площадки и формат">
      {items.map((item) => (
        <li
          key={item.label}
          className={`rounded-full border px-3 py-1 text-xs font-semibold ${item.color}`}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
}
