import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
import { TelegramButton } from "@/components/TelegramButton";
import { Reveal } from "@/components/Reveal";
import { JsonLd, faqSchema } from "@/components/JsonLd";

export const metadata: Metadata = {
  title: "FAQ",
  description:
    "Безопасность API-ключей, ИИ и человек в ответах, негатив, trial PRO, оплата и отмена подписки.",
};

export default function FaqPage() {
  return (
    <PageShell>
      <JsonLd data={faqSchema(FAQ_ITEMS)} />
      <InnerPageHero
        eyebrow="FAQ"
        title="Частые вопросы"
        description="Безопасность, работа ИИ, тарифы и оплата — коротко и по делу."
      />
      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid gap-12 lg:grid-cols-[1.4fr_0.6fr] lg:gap-16">
          <Reveal>
            <FAQAccordion items={FAQ_ITEMS} />
          </Reveal>
          <Reveal delay={100} className="lg:sticky lg:top-28 lg:self-start">
            <aside className="rounded-3xl bg-brand-900 p-8 text-white">
              <h2 className="text-title text-white">Не нашли ответ?</h2>
              <p className="mt-3 text-body text-brand-100">
                Напишите в поддержку прямо в боте — контекст вашего аккаунта подтянется сам.
              </p>
              <TelegramButton variant="white" className="mt-8 w-full">
                Написать в поддержку
              </TelegramButton>
            </aside>
          </Reveal>
        </div>
      </section>
    </PageShell>
  );
}
