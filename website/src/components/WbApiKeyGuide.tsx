import type { ReactNode } from "react";
import { BOT_USERNAME } from "@/content/constants";

const frame =
  "overflow-hidden rounded-2xl border border-line bg-surface-elevated shadow-xs ring-1 ring-black/[0.03]";

function StepBadge({ n }: { n: number }) {
  return (
    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-700 font-display text-small font-semibold text-white">
      {n}
    </span>
  );
}

function MockTopBar() {
  return (
    <div className={`${frame} p-3`}>
      <div className="flex items-center justify-end gap-2">
        <span className="h-7 w-7 rounded-full bg-surface-muted ring-1 ring-line" aria-hidden />
        <span className="h-7 w-7 rounded-full bg-surface-muted ring-1 ring-line" aria-hidden />
        <div className="flex items-center gap-1 rounded-full bg-brand-50 px-3 py-1.5 ring-1 ring-brand-100">
          <span className="text-[10px] font-medium text-ink-muted">Магазин</span>
          <span className="text-[10px] text-ink-faint">▾</span>
        </div>
      </div>
      <div className="mt-3 rounded-xl border border-line bg-white p-3 shadow-sm">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[10px] font-semibold text-ink">Профиль</span>
          <span className="rounded-full bg-brand-700 px-2.5 py-1 text-[10px] font-semibold text-white">
            Настройки
          </span>
        </div>
        <p className="mt-2 text-[9px] leading-snug text-ink-subtle">ИНН · ID продавца</p>
      </div>
    </div>
  );
}

function MockApiTabs() {
  const tabs = ["Данные", "Пользователи", "Мои данные", "Доступ к API"];
  return (
    <div className={`${frame} p-3`}>
      <p className="font-display text-[11px] font-semibold text-ink">Доступ к API</p>
      <div className="mt-2 flex flex-wrap gap-1 border-b border-line pb-2">
        {tabs.map((t) => (
          <span
            key={t}
            className={`rounded-md px-2 py-0.5 text-[9px] ${
              t === "Доступ к API"
                ? "bg-brand-50 font-semibold text-brand-800 ring-1 ring-brand-200"
                : "text-ink-subtle"
            }`}
          >
            {t}
          </span>
        ))}
      </div>
      <p className="mt-2 text-[9px] leading-snug text-ink-muted">
        Здесь создают ключи для интеграций с кабинетом WB.
      </p>
    </div>
  );
}

function MockTokenName() {
  return (
    <div className={`${frame} p-3`}>
      <label className="text-[9px] font-medium text-ink-muted">Имя токена *</label>
      <div className="mt-1.5 rounded-lg border border-brand-200 bg-brand-50/50 px-2.5 py-2 text-[10px] text-ink">
        Голос бренда — отзывы
      </div>
      <p className="mt-2 text-[9px] text-ink-subtle">Любое понятное вам название.</p>
    </div>
  );
}

function MockScopes() {
  const scopes = ["Контент", "Статистика", "Продвижение", "Вопросы и отзывы"];
  return (
    <div className={`${frame} p-3`}>
      <p className="text-[9px] font-medium text-ink-muted">Категории доступа</p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {scopes.map((s) => (
          <span
            key={s}
            className={`rounded-full px-2 py-0.5 text-[9px] ${
              s === "Вопросы и отзывы"
                ? "bg-brand-700 font-semibold text-white"
                : "bg-surface-muted text-ink-muted ring-1 ring-line"
            }`}
          >
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

function MockCreateBtn() {
  return (
    <div className={`${frame} p-3`}>
      <div className="flex flex-wrap gap-2">
        <span className="inline-flex rounded-full bg-brand-700 px-4 py-2 text-[10px] font-semibold text-white shadow-button">
          Создать токен
        </span>
        <span className="inline-flex rounded-full border border-line px-4 py-2 text-[10px] text-ink-muted">
          Отмена
        </span>
      </div>
    </div>
  );
}

function MockCopyToken() {
  return (
    <div className={`${frame} p-3`}>
      <div className="flex items-start justify-between gap-2">
        <p className="font-display text-[10px] font-semibold text-ink">Голос бренда — отзывы</p>
        <span className="rounded-md bg-brand-50 px-1.5 py-0.5 text-[8px] font-medium text-brand-800">
          Вопросы и отзывы
        </span>
      </div>
      <p className="mt-2 text-[9px] font-medium text-clay-600">
        Скопируйте токен сейчас — после обновления страницы он скроется.
      </p>
      <div className="mt-2 rounded-lg bg-surface-muted px-2 py-2 font-mono text-[8px] leading-relaxed text-ink-muted">
        eyJhbG…<span className="text-ink-faint">••••••••••••</span>…x7Kp
      </div>
      <span className="mt-2 inline-flex items-center gap-1 rounded-full border border-line-strong bg-white px-3 py-1.5 text-[9px] font-semibold text-brand-800">
        <span aria-hidden>⎘</span> Скопировать
      </span>
    </div>
  );
}

function MockBotPaste() {
  return (
    <div className={`${frame} bg-brand-900 p-3 text-white`}>
      <p className="text-[9px] text-brand-200">@{BOT_USERNAME}</p>
      <p className="mt-1 font-display text-[11px] font-semibold">Настройки → Кабинеты WB</p>
      <div className="mt-2 rounded-xl border border-white/15 bg-white/10 px-2.5 py-2 text-[9px] text-brand-100">
        Вставьте API-ключ сюда…
      </div>
      <span className="mt-2 inline-block rounded-full bg-white px-3 py-1 text-[9px] font-semibold text-brand-900">
        Сохранить
      </span>
    </div>
  );
}

const STEPS: { title: string; text: string; visual: ReactNode }[] = [
  {
    title: "Откройте настройки магазина",
    text: "В кабинете Wildberries нажмите на имя магазина вверху справа и выберите «Настройки» в меню профиля.",
    visual: <MockTopBar />,
  },
  {
    title: 'Вкладка «Доступ к API»',
    text: "В разделе настроек перейдите на вкладку «Доступ к API» — там создаются ключи для интеграций.",
    visual: <MockApiTabs />,
  },
  {
    title: "Придумайте имя ключа",
    text: "В поле «Имя токена» введите любое название, чтобы потом узнать ключ в списке — например «Голос бренда — отзывы».",
    visual: <MockTokenName />,
  },
  {
    title: "Категория «Вопросы и отзывы»",
    text: "Отметьте только «Вопросы и отзывы» — этого достаточно боту для загрузки отзывов и отправки ваших ответов.",
    visual: <MockScopes />,
  },
  {
    title: "Создайте токен",
    text: "Нажмите «Создать токен». «Только на чтение» и «Тестовый контур» для нашего бота не включайте.",
    visual: <MockCreateBtn />,
  },
  {
    title: "Скопируйте ключ",
    text: "Сразу нажмите «Скопировать» и сохраните ключ в надёжном месте — после перезагрузки страницы WB его может не показать снова.",
    visual: <MockCopyToken />,
  },
  {
    title: "Вставьте ключ в бота",
    text: `Откройте @${BOT_USERNAME} → «Настройки» → «Кабинеты WB/Ozon» и вставьте ключ. На этом сайте ключ нигде не вводится.`,
    visual: <MockBotPaste />,
  },
];

export function WbApiKeyGuide() {
  return (
    <div className="mt-6 space-y-8 border-t border-line pt-6">
      <div>
        <p className="eyebrow">Wildberries</p>
        <p className="mt-2 max-w-prose text-body text-ink-muted">
          Пошагово — как в личном кабинете продавца. Схемы ниже упрощённые, интерфейс WB может чуть
          отличаться.
        </p>
      </div>
      <ol className="space-y-10">
        {STEPS.map((step, i) => (
          <li key={step.title} className="flex flex-col gap-4 sm:flex-row sm:items-start sm:gap-6">
            <StepBadge n={i + 1} />
            <div className="min-w-0 flex-1">
              <h4 className="font-display text-title font-semibold text-ink">{step.title}</h4>
              <p className="mt-2 text-small leading-relaxed text-ink-muted">{step.text}</p>
            </div>
            <div className="w-full shrink-0 sm:max-w-[220px]">{step.visual}</div>
          </li>
        ))}
      </ol>
      <div className="rounded-2xl bg-surface-muted/80 px-5 py-4 ring-1 ring-line">
        <p className="text-small font-semibold text-ink">Ozon</p>
        <p className="mt-2 text-small leading-relaxed text-ink-muted">
          Ключ создаётся в кабинете продавца Ozon в разделе API / интеграций (Seller API). Нужны права
          на работу с отзывами. Вставка — в том же месте бота: «Настройки» → «Кабинеты WB/Ozon».
        </p>
      </div>
    </div>
  );
}
