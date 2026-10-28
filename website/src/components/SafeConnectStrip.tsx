import Link from "next/link";
import { IconShield } from "./icons";

const items = [
  {
    title: "Ключ только в Telegram",
    text: "На сайте ключ не вводится — только в боте.",
  },
  {
    title: "Храним зашифрованным",
    text: "Нужен лишь для отзывов WB и Ozon, не для других операций.",
  },
  {
    title: "Официальные API",
    text: "Работаем через API маркетплейсов, как в личном кабинете.",
  },
] as const;

export function SafeConnectStrip() {
  return (
    <div className="border-y border-line bg-surface-muted/80">
      <div className="container-page py-6 sm:py-7">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between lg:gap-10">
          <p className="flex items-center gap-2 text-small font-semibold text-ink">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-700 ring-1 ring-brand-100">
              <IconShield className="h-4 w-4" />
            </span>
            Безопасно подключать кабинет
          </p>
          <ul className="grid gap-4 sm:grid-cols-3 sm:gap-6 lg:flex-1">
            {items.map((item) => (
              <li key={item.title} className="text-center sm:text-left">
                <p className="text-small font-semibold text-ink">{item.title}</p>
                <p className="mt-1 text-caption leading-snug text-ink-muted">{item.text}</p>
              </li>
            ))}
          </ul>
          <Link
            href="/faq#api-key"
            className="shrink-0 text-center text-caption font-semibold text-brand-700 underline-offset-2 hover:underline sm:text-left lg:text-right"
          >
            Где взять API-ключ →
          </Link>
        </div>
      </div>
    </div>
  );
}
