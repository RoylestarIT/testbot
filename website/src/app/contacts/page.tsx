import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { BOT_AVATAR, BOT_USERNAME, SUPPORT_EMAIL, SUPPORT_TG, SUPPORT_TG_URL } from "@/content/constants";
import { TelegramButton } from "@/components/TelegramButton";
import { Button } from "@/components/Button";
import { Reveal } from "@/components/Reveal";
import { IconArrowRight } from "@/components/icons";

export const metadata: Metadata = {
  title: "Контакты и поддержка",
  description: "Как связаться с командой «Голос бренда»: Telegram и почта.",
};

export default function ContactsPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Контакты"
        title="Мы на связи"
        description="Пишите как удобно. Быстрее всего — в Telegram: отвечают живые люди, без роботов и очередей."
      />
      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid max-w-4xl gap-5 md:grid-cols-2">
          <Reveal>
            <div className="flex h-full flex-col rounded-3xl bg-brand-900 p-8 text-white sm:p-10">
              <div className="flex items-center justify-between gap-4">
                <p className="text-caption font-semibold uppercase tracking-[0.14em] text-brand-300">
                  Рекомендуем
                </p>
                {/* eslint-disable-next-line @next/next/no-img-element -- static export, no image optimizer */}
                <img
                  src={BOT_AVATAR}
                  alt={`Аватар бота @${BOT_USERNAME}`}
                  width={56}
                  height={56}
                  className="h-14 w-14 rounded-full ring-4 ring-white/10"
                />
              </div>
              <h2 className="mt-4 text-headline text-white">Telegram</h2>
              <p className="mt-3 flex-1 text-body text-brand-100">
                В боте @{BOT_USERNAME} откройте «Поддержка» или напишите нам напрямую —{" "}
                <a
                  href={SUPPORT_TG_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-white underline decoration-white/30 underline-offset-4 hover:decoration-white"
                >
                  @{SUPPORT_TG}
                </a>
                . Обычно отвечаем в течение рабочего дня.
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
                Счета, договоры и всё, что удобнее обсудить письмом.
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
