import Link from "next/link";
import { PageShell } from "@/components/PageShell";
import { TelegramButton } from "@/components/TelegramButton";

export default function NotFound() {
  return (
    <PageShell>
      <div className="mx-auto max-w-lg px-4 py-24 text-center sm:px-6">
        <p className="eyebrow">404</p>
        <h1 className="mt-2 font-display text-display text-ink">Страница не найдена</h1>
        <p className="mt-3 text-body text-ink-muted">
          Возможно, ссылка устарела. Перейдите на главную или откройте бота в Telegram.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-full bg-brand-700 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-800"
          >
            На главную
          </Link>
          <TelegramButton variant="secondary">Открыть в Telegram</TelegramButton>
        </div>
      </div>
    </PageShell>
  );
}
