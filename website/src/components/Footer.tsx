import Link from "next/link";
import {
  BOT_USERNAME,
  BRAND,
  BRAND_TECH,
  PRICING_UPDATED,
  SUPPORT_EMAIL,
} from "@/lib/constants";
import { TelegramButton } from "./TelegramButton";

export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-900 text-slate-300">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="flex flex-col gap-8 md:flex-row md:justify-between">
          <div className="max-w-sm">
            <p className="text-lg font-semibold text-white">{BRAND}</p>
            <p className="mt-2 text-sm leading-relaxed">
              Co-pilot для отзывов WB и Ozon в Telegram. Контроль текста у вас —
              рутину забирает бот.
            </p>
            <div className="mt-4">
              <TelegramButton variant="secondary" trackSite>
                Начать бесплатно
              </TelegramButton>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-8 text-sm sm:grid-cols-3">
            <div>
              <p className="font-medium text-white">Продукт</p>
              <ul className="mt-3 space-y-2">
                <li>
                  <Link href="/how-it-works" className="hover:text-white">
                    Как работает
                  </Link>
                </li>
                <li>
                  <Link href="/pricing" className="hover:text-white">
                    Тарифы
                  </Link>
                </li>
                <li>
                  <Link href="/changelog" className="hover:text-white">
                    Что нового
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-white">Компания</p>
              <ul className="mt-3 space-y-2">
                <li>
                  <Link href="/for-who" className="hover:text-white">
                    Для кого
                  </Link>
                </li>
                <li>
                  <Link href="/contacts" className="hover:text-white">
                    Контакты
                  </Link>
                </li>
                <li>
                  <Link href="/faq" className="hover:text-white">
                    FAQ
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-white">Документы</p>
              <ul className="mt-3 space-y-2">
                <li>
                  <Link href="/privacy" className="hover:text-white">
                    Конфиденциальность
                  </Link>
                </li>
                <li>
                  <Link href="/terms" className="hover:text-white">
                    Соглашение
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-2 border-t border-slate-700 pt-6 text-xs text-slate-500">
          <p>
            Бот: @{BOT_USERNAME} · Поддержка: бот → «Поддержка» · Email:{" "}
            <a href={`mailto:${SUPPORT_EMAIL}`} className="underline hover:text-slate-300">
              {SUPPORT_EMAIL}
            </a>
          </p>
          <p>
            Цены актуальны в боте · на лендинге обновлено {PRICING_UPDATED}. Оплата
            Stars — сумма отображается в боте (к ₽ может применяться наценка).
          </p>
          <p>
            © {new Date().getFullYear()} {BRAND}. Техническое имя: {BRAND_TECH}.
          </p>
        </div>
      </div>
    </footer>
  );
}
