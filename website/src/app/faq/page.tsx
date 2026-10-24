import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
import { TelegramButton } from "@/components/TelegramButton";

export const metadata: Metadata = {
  title: "FAQ",
  description:
    "Безопасность API-ключей, ИИ и человек в ответах, негатив, trial PRO, оплата и отмена подписки.",
};

export default function FaqPage() {
  return (
    <PageShell>
      <InnerPageHero title="Частые вопросы" />
      <div className="container-page max-w-3xl section-y !pt-10">
        <FAQAccordion items={FAQ_ITEMS} />
        <p className="mt-8 text-center text-sm text-slate-600">
          Не нашли ответ? Напишите в бота → «Поддержка» — контекст подтянется автоматически.
        </p>
        <div className="mt-6 flex justify-center">
          <TelegramButton className="!rounded-full">Открыть поддержку в боте</TelegramButton>
        </div>
      </div>
    </PageShell>
  );
}
