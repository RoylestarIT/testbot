import Link from "next/link";

/** Дисклеймер оплаты — футер и блоки тарифов. */
export function LegalDisclaimer({ className = "" }: { className?: string }) {
  return (
    <p className={`text-caption leading-relaxed text-ink-subtle ${className}`}>
      Оплата тарифа означает согласие с условиями{" "}
      <Link href="/terms" className="text-brand-700 underline-offset-2 hover:underline">
        Публичной оферты
      </Link>{" "}
      и{" "}
      <Link href="/privacy" className="text-brand-700 underline-offset-2 hover:underline">
        Политикой конфиденциальности
      </Link>
      . Услуга предоставляется в электронном виде (доступ к функционалу Telegram-бота).
    </p>
  );
}

export function LegalDisclaimerFooter({ className = "" }: { className?: string }) {
  return (
    <p className={`text-caption leading-relaxed text-footer-muted ${className}`}>
      Оплата тарифа означает согласие с условиями{" "}
      <Link href="/terms" className="text-footer-text underline-offset-2 hover:underline">
        Публичной оферты
      </Link>{" "}
      и{" "}
      <Link href="/privacy" className="text-footer-text underline-offset-2 hover:underline">
        Политикой конфиденциальности
      </Link>
      . Услуга предоставляется в электронном виде (доступ к функционалу Telegram-бота).
    </p>
  );
}
