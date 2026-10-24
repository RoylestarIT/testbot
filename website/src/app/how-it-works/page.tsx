import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramMockup } from "@/components/TelegramMockup";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  title: "Как работает бот для отзывов WB и Ozon",
  description:
    "Подключение кабинета, синхронизация, три варианта ответа ИИ, publish в API или копия в личный кабинет — пошагово в Telegram.",
};

export default function HowItWorksPage() {
  return (
    <PageShell>
      <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
        <SectionHeading
          title="Как это работает"
          description="Вся работа — в Telegram. Лендинг только объясняет; личный кабинет бота не дублируем на сайте."
        />

        <div className="mt-14 grid gap-12 lg:grid-cols-2 lg:items-center">
          <TelegramMockup />
          <ol className="space-y-8">
            {[
              {
                title: "Подключить кабинет",
                body: "Добавьте API-ключ WB или Ozon в боте. Ключи шифруются и не запрашиваются на этом сайте.",
              },
              {
                title: "Sync и уведомления",
                body: "Новые отзывы приходят push-сообщением. Можно отложить (snooze) или получить дайджест.",
              },
              {
                title: "3 варианта ответа",
                body: "ИИ учитывает tone of voice, стоп-слова и контекст товара. Вы выбираете или правите текст.",
              },
              {
                title: "Publish или копия",
                body: "PRO: отправка в Seller API из бота, авто только 4–5★. Lite/Free: копируете готовый ответ в кабинет маркетплейса.",
              },
            ].map((step, i) => (
              <li key={step.title} className="flex gap-4">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white">
                  {i + 1}
                </span>
                <div>
                  <h3 className="font-semibold text-slate-900">{step.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-slate-600">{step.body}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>

        <div className="mt-16 rounded-2xl bg-slate-900 p-8 text-center text-white">
          <h2 className="text-xl font-semibold">Поток в одном месте</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-slate-300">
            Маркетплейс → sync → Telegram → черновики → человек → publish/копия → покупатель
            видит ответ
          </p>
          <div className="mt-6">
            <TelegramButton variant="secondary">Открыть в Telegram</TelegramButton>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
