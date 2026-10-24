import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { BOT_USERNAME, SUPPORT_EMAIL } from "@/content/constants";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  title: "Контакты и поддержка",
  description: "Поддержка «Голос бренда» через Telegram-бот и email.",
};

export default function ContactsPage() {
  return (
    <PageShell>
      <div className="mx-auto max-w-xl px-4 py-14 sm:px-6">
        <SectionHeading
          title="Контакты"
          description="Основной канал — бот: быстрее всего поможем с контекстом вашего аккаунта."
        />
        <div className="mt-10 space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
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
                className="text-blue-600 hover:underline"
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
