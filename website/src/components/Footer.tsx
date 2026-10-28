import type { ReactNode } from "react";
import Link from "next/link";
import {
  BOT_URL,
  BOT_USERNAME,
  BRAND,
  HAS_SUPPORT_EMAIL,
  LEGAL_OPERATOR,
  PAYMENT_METHODS_LINE,
  PRICING_UPDATED,
  SUPPORT_EMAIL,
  SUPPORT_TG,
  SUPPORT_TG_URL,
} from "@/content/constants";
import { Logo } from "./Logo";
import { LegalDisclaimerFooter } from "./LegalDisclaimer";
import { TelegramButton } from "./TelegramButton";

function FooterMetaCard({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-footer-border bg-white/[0.04] p-5 sm:p-6">
      <p className="text-caption font-semibold uppercase tracking-[0.12em] text-footer-text">{title}</p>
      <div className="mt-3 space-y-2 text-small leading-relaxed text-footer-muted">{children}</div>
    </div>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-line bg-footer-bg text-footer-text">
      <div className="container-page py-16 sm:py-20">
        <div className="flex flex-col gap-14 lg:flex-row lg:justify-between">
          <div className="max-w-sm">
            <Logo inverted />
            <p className="mt-5 text-body text-footer-text">
              Помогаем селлерам WB и Ozon отвечать на отзывы быстро и по-человечески. Прямо в Telegram.
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

        <div className="mt-16 grid gap-4 border-t border-footer-border pt-10 sm:grid-cols-2 lg:grid-cols-3">
          <FooterMetaCard title="Связь">
            <p>
              Бот{" "}
              <a href={BOT_URL} className="font-medium text-footer-text underline-offset-2 hover:text-white hover:underline">
                @{BOT_USERNAME}
              </a>
            </p>
            <p>
              Поддержка{" "}
              <a
                href={SUPPORT_TG_URL}
                className="font-medium text-footer-text underline-offset-2 hover:text-white hover:underline"
              >
                @{SUPPORT_TG}
              </a>
            </p>
            {HAS_SUPPORT_EMAIL ? (
              <p>
                Email{" "}
                <a
                  href={`mailto:${SUPPORT_EMAIL}`}
                  className="font-medium text-footer-text underline-offset-2 hover:text-white hover:underline"
                >
                  {SUPPORT_EMAIL}
                </a>
              </p>
            ) : (
              <p className="text-footer-muted">Почта для документов подключается</p>
            )}
          </FooterMetaCard>

          <FooterMetaCard title="Оператор и тарифы">
            <p>{LEGAL_OPERATOR}</p>
            <p className="text-caption">
              Цены на {PRICING_UPDATED}. Точную сумму бот покажет перед оплатой.
            </p>
            <p className="text-caption">Оплата: {PAYMENT_METHODS_LINE}.</p>
          </FooterMetaCard>

          <FooterMetaCard title="Документы">
            <p>
              <Link href="/terms" className="text-footer-text underline-offset-2 hover:text-white hover:underline">
                Публичная оферта
              </Link>
            </p>
            <p>
              <Link href="/privacy" className="text-footer-text underline-offset-2 hover:text-white hover:underline">
                Политика конфиденциальности
              </Link>
            </p>
            <p className="text-caption pt-1">Услуга — доступ к функционалу Telegram-бота.</p>
          </FooterMetaCard>
        </div>

        <div className="mt-8 space-y-4 border-t border-footer-border pt-8">
          <LegalDisclaimerFooter className="max-w-3xl text-caption" />
          <p className="text-caption text-footer-muted">
            © {new Date().getFullYear()} {BRAND}. Сделано для селлеров WB и Ozon.
          </p>
        </div>
      </div>
    </footer>
  );
}
