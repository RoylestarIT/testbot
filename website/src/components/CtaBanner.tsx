import { Button } from "./Button";
import { Reveal } from "./Reveal";
import { TelegramButton } from "./TelegramButton";
import { IconArrowRight } from "./icons";

export function CtaBanner({
  title = "Первый ответ — уже сегодня",
  description = "Подключите кабинет за пару минут. Бесплатно и без карты.",
  cta = "Открыть бота в Telegram",
  showCalculatorLink = false,
}: {
  title?: string;
  description?: string;
  cta?: string;
  showCalculatorLink?: boolean;
}) {
  return (
    <section className="px-5 py-20 sm:px-8 sm:py-24">
      <Reveal className="mx-auto max-w-6xl">
        <div className="relative overflow-hidden rounded-4xl bg-cta-gradient px-6 py-20 text-center sm:px-12 sm:py-24">
          <div
            className="mask-fade-b absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-grid"
            aria-hidden
          />
          <div className="relative mx-auto max-w-2xl">
            <h2 className="text-headline text-white sm:text-display-lg">{title}</h2>
            <p className="mx-auto mt-6 max-w-md text-body-lg text-brand-100">{description}</p>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
              <TelegramButton variant="white" size="lg" trackSite>
                {cta}
              </TelegramButton>
              {showCalculatorLink && (
                <Button
                  href="/#calculator"
                  size="lg"
                  variant="secondary"
                  trailing={<IconArrowRight />}
                  className="border-white/25 bg-white/10 text-white shadow-none hover:border-white/40 hover:bg-white/15 hover:text-white"
                >
                  Посчитать экономию
                </Button>
              )}
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
