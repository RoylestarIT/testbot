import { SUPPORT_TG, SUPPORT_TG_URL } from "@/content/constants";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

function IconLock() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <rect x="5" y="10.5" width="14" height="10" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

function IconHand() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path
        d="M12 21c4.4 0 8-3.1 8-7V9.5M4 13V8.5a2 2 0 0 1 4 0V12m0-1V5.5a2 2 0 0 1 4 0V11m0-.5V6.5a2 2 0 0 1 4 0V11m0-1.5a2 2 0 0 1 4 0M4 13c0 4.4 3.6 8 8 8"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconCalendar() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <rect x="4" y="5.5" width="16" height="15" rx="2.5" stroke="currentColor" strokeWidth="1.6" />
      <path d="M4 10h16M8.5 3.5v4M15.5 3.5v4M9 15l2 2 4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconChat() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden>
      <path
        d="M5 18.5V7a2.5 2.5 0 0 1 2.5-2.5h9A2.5 2.5 0 0 1 19 7v7a2.5 2.5 0 0 1-2.5 2.5H8.5L5 18.5z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M9 10.5h6M9 13h3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}

const items = [
  {
    icon: <IconLock />,
    title: "Ключи под замком",
    text: "Ключ от кабинета хранится зашифрованным и нужен только для отзывов. На сайте его не просим.",
  },
  {
    icon: <IconHand />,
    title: "Последнее слово — ваше",
    text: "На плохие отзывы бот сам не отвечает никогда. Только после того, как вы посмотрели и согласились.",
  },
  {
    icon: <IconCalendar />,
    title: "Без автосписаний",
    text: "Подписка не продлевается сама. Не подошло — просто не платите за следующий месяц.",
  },
  {
    icon: <IconChat />,
    title: "Живая поддержка",
    text: "Отвечают люди, а не автоответчик. Пишите в бота или напрямую",
    link: { href: SUPPORT_TG_URL, label: `@${SUPPORT_TG}` },
  },
];

export function TrustSection() {
  return (
    <section className="section-y">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Спокойно и честно"
            title="Почему нам доверяют свои кабинеты"
            description="Мы понимаем, что подключать сторонний сервис к магазину — шаг. Поэтому вот как всё устроено."
          />
        </Reveal>
        <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
          {items.map((item, i) => (
            <Reveal key={item.title} delay={i * 70}>
              <div className="card-hover group h-full p-7">
                <div className="icon-tile group-hover:bg-brand-700 group-hover:text-white group-hover:ring-brand-700">
                  {item.icon}
                </div>
                <h3 className="mt-6 text-title">{item.title}</h3>
                <p className="mt-3 text-body text-ink-muted">
                  {item.text}
                  {item.link && (
                    <>
                      {" "}
                      <a
                        href={item.link.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-brand-700 hover:underline"
                      >
                        {item.link.label}
                      </a>
                      .
                    </>
                  )}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
