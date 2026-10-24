import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { LegalDocument } from "@/components/LegalDocument";
import { getTermsSections } from "@/content/legal";

export const metadata: Metadata = {
  title: "Пользовательское соглашение",
  description: "Условия использования сервиса «Голос бренда» в Telegram.",
};

export default function TermsPage() {
  return (
    <PageShell>
      <LegalDocument
        title="Пользовательское соглашение"
        subtitle="Сервис «Голос бренда» в Telegram"
        sections={getTermsSections()}
      />
    </PageShell>
  );
}
