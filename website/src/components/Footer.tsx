import Link from "next/link";
import {
  BOT_USERNAME,
  BRAND,
  BRAND_TECH,
  PRICING_UPDATED,
  SUPPORT_EMAIL,
} from "@/content/constants";
import { Logo } from "./Logo";
import { LegalDisclaimerFooter } from "./LegalDisclaimer";
import { TelegramButton } from "./TelegramButton";

export function Footer() {
  return (
    <footer className="border-t border-line bg-footer-bg text-footer-text">
      <div className="container-page py-16 sm:py-20">
        <div className="flex flex-col gap-14 lg:flex-row lg:justify-between">
          <div className="max-w-sm">
            <Logo inverted />
            <p className="mt-5 text-body text-footer-text">
              Помощник для ответов на отзывы WB и Ozon в Telegram. Текст решаете вы —
              рутину берёт бот.
            </p>
            <div className="mt-7">
              <TelegramButton variant="white" trackSite>
                Начать бесплатно
              </TelegramButton>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-10 text-small sm:grid-cols-3 sm:gap-16">
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

        <div className="mt-16 flex flex-col gap-2 border-t border-footer-border pt-8 text-caption text-footer-muted">
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
          <LegalDisclaimerFooter className="max-w-3xl" />
          <p className="pt-2">
            © {new Date().getFullYear()} {BRAND}. Техническое имя: {BRAND_TECH}.
          </p>
        </div>
      </div>
    </footer>
  );
}
