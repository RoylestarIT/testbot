import type { Metadata } from "next";
import { canonical } from "@/content/constants";
import { PageShell } from "@/components/PageShell";
import { LegalDocument } from "@/components/LegalDocument";
import { getPrivacySections } from "@/content/legal";

export const metadata: Metadata = {
  alternates: canonical("/privacy"),
  title: "Политика конфиденциальности",
  description: "Обработка персональных данных сервиса «Голос бренда» для селлеров WB и Ozon.",
};

export default function PrivacyPage() {
  return (
    <PageShell>
      <LegalDocument
        title="Политика конфиденциальности"
        subtitle="Telegram-бот для продавцов Wildberries и Ozon"
        sections={getPrivacySections()}
      />
    </PageShell>
  );
}
