"use client";

import { useId, useState } from "react";
import { PRICES } from "@/content/constants";
import { TelegramButton } from "./TelegramButton";

const PAY_PER_ANSWER_RUB = 2;
const BOT_SECONDS_PER_REVIEW = 30;
const FREE_MONTHLY_LIMIT = 150;

function formatNumber(n: number) {
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(n);
}

function formatHours(h: number) {
  if (h < 1) return `${Math.round(h * 60)} мин`;
  return `${new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 1 }).format(h)} ч`;
}

function recommend(reviews: number) {
  if (reviews <= FREE_MONTHLY_LIMIT)
    return { plan: "Free", price: 0, why: "До ~5 ответов в день хватит бесплатного тарифа." };
  if (reviews <= 500)
    return { plan: "Lite", price: PRICES.lite.rub, why: "Безлимит ответов по фиксированной цене." };
  return {
    plan: "PRO",
    price: PRICES.pro.rub,
    why: "Публикация из бота и автоответы на 4–5★ снимут основной поток.",
  };
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  suffix,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  onChange: (v: number) => void;
}) {
  const id = useId();
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <label htmlFor={id} className="text-small font-medium text-ink-muted">
          {label}
        </label>
        <output htmlFor={id} className="font-display text-title font-semibold tabular-nums text-ink">
          {formatNumber(value)} <span className="text-small font-normal text-ink-subtle">{suffix}</span>
        </output>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="range mt-4 w-full"
        style={{ "--range-pct": `${pct}%` } as React.CSSProperties}
      />
    </div>
  );
}

export function SavingsCalculator() {
  const [reviews, setReviews] = useState(300);
  const [minutes, setMinutes] = useState(3);

  const manualHours = (reviews * minutes) / 60;
  const botHours = (reviews * BOT_SECONDS_PER_REVIEW) / 3600;
  const savedHours = Math.max(0, manualHours - botHours);
  const payPerAnswer = reviews * PAY_PER_ANSWER_RUB;
  const rec = recommend(reviews);

  return (
    <div className="grid overflow-hidden rounded-4xl border border-line bg-surface shadow-card lg:grid-cols-[1.05fr_0.95fr]">
      <div className="p-8 sm:p-10 lg:p-12">
        <p className="eyebrow">Калькулятор</p>
        <h3 className="mt-4 text-headline">Сколько времени вы вернёте</h3>
        <p className="mt-3 text-body text-ink-muted">
          Подвиньте ползунки под свой магазин — посчитаем экономию.
        </p>
        <div className="mt-10 space-y-9">
          <Slider
            label="Отзывов в месяц"
            value={reviews}
            min={30}
            max={2000}
            step={10}
            suffix="шт."
            onChange={setReviews}
          />
          <Slider
            label="Минут на один ответ вручную"
            value={minutes}
            min={1}
            max={10}
            step={1}
            suffix="мин"
            onChange={setMinutes}
          />
        </div>
        <p className="mt-10 text-caption text-ink-subtle">
          Оценка: с ботом ≈{BOT_SECONDS_PER_REVIEW} секунд на выбор и правку черновика, оплата
          за ответ на рынке ≈{PAY_PER_ANSWER_RUB} ₽. Не является гарантией результата.
        </p>
      </div>

      <div className="flex flex-col bg-brand-900 p-8 text-white sm:p-10 lg:p-12">
        <p className="text-small text-brand-200">Вы сэкономите</p>
        <p
          className="mt-2 font-display text-display-lg font-semibold tabular-nums text-white sm:text-display-xl"
          aria-live="polite"
        >
          {formatHours(savedHours)}
        </p>
        <p className="text-body text-brand-200">в месяц на ответах</p>

        <dl className="mt-10 grid grid-cols-2 gap-px overflow-hidden rounded-2xl bg-white/10">
          <div className="bg-brand-900/60 p-5">
            <dt className="text-caption text-brand-300">Вручную</dt>
            <dd className="mt-1 font-display text-title tabular-nums">{formatHours(manualHours)}</dd>
          </div>
          <div className="bg-brand-900/60 p-5">
            <dt className="text-caption text-brand-300">С ботом</dt>
            <dd className="mt-1 font-display text-title tabular-nums">{formatHours(botHours)}</dd>
          </div>
          <div className="bg-brand-900/60 p-5">
            <dt className="text-caption text-brand-300">Оплата за ответ</dt>
            <dd className="mt-1 font-display text-title tabular-nums">{formatNumber(payPerAnswer)} ₽</dd>
          </div>
          <div className="bg-brand-900/60 p-5">
            <dt className="text-caption text-brand-300">Тариф {rec.plan}</dt>
            <dd className="mt-1 font-display text-title tabular-nums">{formatNumber(rec.price)} ₽</dd>
          </div>
        </dl>

        <div className="mt-8 flex-1 rounded-2xl bg-white/5 p-5 ring-1 ring-white/10">
          <p className="text-small text-brand-100">
            Подходит тариф <span className="font-semibold text-white">{rec.plan}</span>. {rec.why}
          </p>
        </div>

        <TelegramButton variant="white" size="lg" trackSite className="mt-8 w-full">
          {rec.plan === "Free" ? "Начать бесплатно" : `Попробовать ${rec.plan}`}
        </TelegramButton>
      </div>
    </div>
  );
}
