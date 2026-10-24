import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { BOT_USERNAME, SUPPORT_EMAIL, canonical } from "@/content/constants";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  alternates: canonical("/contacts"),
  title: "Контакты и поддержка",
  description: "Поддержка «Голос бренда» через Telegram-бот и email.",
};

export default function ContactsPage() {
  return (
    <PageShell>
      <InnerPageHero
        title="Контакты"
        description="Основной канал — бот: быстрее всего поможем с контекстом вашего аккаунта."
      />
      <div className="container-page max-w-xl section-y !pt-10">
        <div className="card space-y-6 p-8 sm:p-9">
          <div>
            <h2 className="text-sm font-semibold uppercase text-slate-500">Telegram</h2>
            <p className="mt-2 text-slate-900">
              @{BOT_USERNAME} → меню «Поддержка»
            </p>
            <div className="mt-4">
              <TelegramButton variant="primary">Написать в бота</TelegramButton>
            </div>
          </div>
          <div>
            <h2 className="text-sm font-semibold uppercase text-slate-500">Email</h2>
            <p className="mt-2">
              <a
                href={`mailto:${SUPPORT_EMAIL}`}
                className="font-medium text-brand-600 hover:text-brand-700 hover:underline"
              >
                {SUPPORT_EMAIL}
              </a>
            </p>
            <p className="mt-1 text-xs text-slate-500">Placeholder — замените в env при деплое.</p>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
