import Link from "next/link";
import {
  BOT_USERNAME,
  BRAND,
  BRAND_TECH,
  PRICING_UPDATED,
  SUPPORT_EMAIL,
} from "@/content/constants";
import { Logo } from "./Logo";
import { TelegramButton } from "./TelegramButton";

export function Footer() {
  return (
    <footer className="border-t border-line bg-footer-bg text-footer-text">
      <div className="container-page py-14">
        <div className="flex flex-col gap-10 lg:flex-row lg:justify-between">
          <div className="max-w-sm">
            <Logo inverted />
            <p className="mt-4 text-body leading-relaxed text-footer-text">
              Co-pilot для отзывов WB и Ozon в Telegram. Контроль текста у вас —
              рутину забирает бот.
            </p>
            <div className="mt-5">
              <TelegramButton variant="white" trackSite className="!rounded-full">
                Начать бесплатно
              </TelegramButton>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-8 text-sm sm:grid-cols-3">
            <div>
              <p className="font-display font-semibold text-white">Продукт</p>
              <ul className="mt-4 space-y-2.5">
                {[
                  ["/how-it-works", "Как работает"],
                  ["/pricing", "Тарифы"],
                  ["/changelog", "Что нового"],
                ].map(([href, label]) => (
                  <li key={href}>
                    <Link href={href} className="transition hover:text-white">
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-display font-semibold text-white">Компания</p>
              <ul className="mt-4 space-y-2.5">
                {[
                  ["/for-who", "Для кого"],
                  ["/contacts", "Контакты"],
                  ["/faq", "FAQ"],
                ].map(([href, label]) => (
                  <li key={href}>
                    <Link href={href} className="transition hover:text-white">
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-display font-semibold text-white">Документы</p>
              <ul className="mt-4 space-y-2.5">
                {[
                  ["/privacy", "Конфиденциальность"],
                  ["/terms", "Соглашение"],
                ].map(([href, label]) => (
                  <li key={href}>
                    <Link href={href} className="transition hover:text-white">
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-2 border-t border-footer-border pt-8 text-caption text-footer-muted">
          <p>
            Бот: @{BOT_USERNAME} · Поддержка: бот → «Поддержка» ·{" "}
            <a href={`mailto:${SUPPORT_EMAIL}`} className="underline hover:text-footer-text">
              {SUPPORT_EMAIL}
            </a>
          </p>
          <p>
            Цены актуальны в боте · на лендинге {PRICING_UPDATED}. Оплата Stars — сумма в
            боте.
          </p>
          <p>
            © {new Date().getFullYear()} {BRAND}. Техническое имя: {BRAND_TECH}.
          </p>
        </div>
      </div>
    </footer>
  );
}
