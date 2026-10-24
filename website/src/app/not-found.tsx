import { PageShell } from "@/components/PageShell";
import { Button } from "@/components/Button";
import { TelegramButton } from "@/components/TelegramButton";

export default function NotFound() {
  return (
    <PageShell>
      <div className="mx-auto max-w-lg px-5 py-32 text-center">
        <p className="eyebrow">Ошибка 404</p>
        <h1 className="mt-4 text-display">Такой страницы нет</h1>
        <p className="mt-5 text-body-lg text-ink-muted">
          Возможно, ссылка устарела. Вернитесь на главную или откройте бота.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          <Button href="/">На главную</Button>
          <TelegramButton variant="secondary">Открыть бота</TelegramButton>
        </div>
      </div>
    </PageShell>
  );
}
