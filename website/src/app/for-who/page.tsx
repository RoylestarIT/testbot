import type { Metadata } from "next";
import { canonical } from "@/content/constants";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  alternates: canonical("/for-who"),
  title: "Для кого сервис",
  description:
    "Селлеры Wildberries и Ozon с 30–1000+ отзывами в месяц, Telegram-first workflow и контроль негатива.",
};

export default function ForWhoPage() {
  return (
    <PageShell>
      <InnerPageHero
        title="Для кого «Голос бренда»"
        description="Продавцы на WB и Ozon в РФ и Беларуси, которым важны скорость ответов и контроль тона."
      />
      <div className="container-page section-y !pt-10">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="card border-emerald-200/80 bg-emerald-50/50 p-8">
            <h2 className="text-lg font-semibold text-green-900">Наш клиент</h2>
            <ul className="mt-4 space-y-3 text-sm text-green-950">
              <li>· ~30–1000+ отзывов в месяц на WB и/или Ozon</li>
              <li>· Работаете сами или маленькая команда — некому сидеть в отзывах весь день</li>
              <li>· Хотите Telegram-first: уведомление → черновик → правка → publish или копия</li>
              <li>· Важен контроль: негатив 1–3★ только с подтверждения человека</li>
              <li>· Нужны несколько кабинетов и tone-профилей (Lite/PRO)</li>
            </ul>
          </div>
          <div className="card border-amber-200/80 bg-amber-50/50 p-8">
            <h2 className="text-lg font-semibold text-amber-950">Скорее не к нам</h2>
            <ul className="mt-4 space-y-3 text-sm text-amber-950">
              <li>· Нужен только Яндекс Маркет — пока не поддерживаем</li>
              <li>· Требуется 100% автомат на все звёзды без участия человека</li>
              <li>· Нужна тяжёлая BI без работы с отзывами в Telegram</li>
              <li>· Нужен отдельный web-кабинет вместо бота — мы сознательно Telegram-first</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 text-center">
          <TelegramButton trackSite>Начать бесплатно в Telegram</TelegramButton>
        </div>
      </div>
    </PageShell>
  );
}
