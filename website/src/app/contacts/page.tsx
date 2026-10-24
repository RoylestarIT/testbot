import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { BOT_USERNAME, SUPPORT_EMAIL } from "@/content/constants";
import { TelegramButton } from "@/components/TelegramButton";
import { Button } from "@/components/Button";
import { Reveal } from "@/components/Reveal";
import { IconArrowRight } from "@/components/icons";

export const metadata: Metadata = {
  title: "Контакты и поддержка",
  description: "Поддержка «Голос бренда» через Telegram-бот и email.",
};

export default function ContactsPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Контакты"
        title="Мы на связи"
        description="Быстрее всего ответим в боте — там сразу видно ваш аккаунт и тариф."
      />
      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid max-w-4xl gap-5 md:grid-cols-2">
          <Reveal>
            <div className="flex h-full flex-col rounded-3xl bg-brand-900 p-8 text-white sm:p-10">
              <p className="text-caption font-semibold uppercase tracking-[0.14em] text-brand-300">
                Рекомендуем
              </p>
              <h2 className="mt-4 text-headline text-white">Telegram</h2>
              <p className="mt-3 flex-1 text-body text-brand-100">
                @{BOT_USERNAME} → меню «Поддержка». Обычно отвечаем в течение рабочего дня.
              </p>
              <TelegramButton variant="white" className="mt-8 w-fit">
                Написать в бота
              </TelegramButton>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <div className="card flex h-full flex-col p-8 sm:p-10">
              <p className="eyebrow">Для документов</p>
              <h2 className="mt-4 text-headline">Email</h2>
              <p className="mt-3 flex-1 text-body text-ink-muted">
                Счета, договоры и вопросы, которые удобнее решать письмом.
              </p>
              <Button
                href={`mailto:${SUPPORT_EMAIL}`}
                external
                variant="secondary"
                className="mt-8 w-fit"
                trailing={<IconArrowRight />}
              >
                {SUPPORT_EMAIL}
              </Button>
            </div>
          </Reveal>
        </div>
      </section>
    </PageShell>
  );
}
