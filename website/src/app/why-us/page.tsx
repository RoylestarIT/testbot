import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { PRICES } from "@/content/constants";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  title: "Почему мы",
  description:
    "Co-pilot в Telegram vs типичные сервисы: фикс подписка, WB+Ozon, контроль негатива, publish из бота.",
};

export default function WhyUsPage() {
  return (
    <PageShell>
      <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6">
        <SectionHeading
          eyebrow="Почему мы"
          title="Время, деньги и лояльность — в одном Telegram"
        />

        <article className="mt-10 space-y-8 text-ink-muted">
          <blockquote className="rounded-xl border-l-4 border-brand-500 bg-brand-50/60 p-4 text-body text-ink-muted">
            Отзывы не должны съедать ваш день. «Голос бренда» забирает рутину: подтягиваем
            WB/Ozon, предлагаем 3 варианта ответа — вы решаете, что увидит покупатель.
          </blockquote>

          <section>
            <h2 className="font-display text-title text-ink">Экономия времени</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-body">
              <li>Очередь в Telegram — без прыжков между кабинетами и таблицами</li>
              <li>ИИ готовит черновики — правка за минуты</li>
              <li>PRO: publish в API и авто только на 4–5★</li>
            </ul>
          </section>

          <section>
            <h2 className="font-display text-title text-ink">Экономия на людях</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-body">
              <li>
                Отдельный сотрудник «только на отзывы» — часто{" "}
                <strong>30–80 тыс. ₽</strong> и выше в месяц на рынке (без гарантий экономии
                для вашего кейса)
              </li>
              <li>
                Подписка <strong>{PRICES.lite.rub} ₽</strong> /{" "}
                <strong>{PRICES.pro.rub} ₽</strong> (<strong>{PRICES.lite.byn}</strong> /{" "}
                <strong>{PRICES.pro.byn} BYN</strong>) — фикс, без оплаты за каждый ответ как
                в pay-per-answer (~1–3 ₽/ответ)
              </li>
            </ul>
          </section>

          <section>
            <h2 className="font-display text-title text-ink">Лояльность и продажи</h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-body">
              <li>Живой ответ повышает доверие к карточке</li>
              <li>Негатив 1–3★ только с вашего подтверждения</li>
              <li>Единый tone на WB и Ozon</li>
            </ul>
          </section>

          <section>
            <h2 className="font-display text-title text-ink">
              Сравнение с рынком (без имён конкурентов)
            </h2>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-body">
              <li>
                <strong>Мы</strong> — co-pilot в Telegram: sync → ответы → publish или копия
              </li>
              <li>
                <strong>Часто</strong> — отдельный сайт, только WB или перегруженный SaaS
              </li>
              <li>
                <strong>Часто</strong> — оплата за каждый ответ вместо предсказуемого фикса
              </li>
            </ul>
          </section>
        </article>

        <div className="mt-10 flex justify-center">
          <TelegramButton trackSite>Попробовать в боте</TelegramButton>
        </div>
      </div>
    </PageShell>
  );
}
