"use client";

import { useEffect, useState } from "react";
import {
  LIVE_METRICS_URL,
  METRICS_JSON_URL,
  pluralSellers,
  type PublicMetrics,
} from "@/content/metrics";

const REFRESH_MS = 10 * 60 * 1000;

function parseMetrics(raw: unknown): PublicMetrics | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const sellers = o.sellersWithCabinet;
  const count =
    typeof sellers === "number" && Number.isFinite(sellers) ? Math.max(0, Math.trunc(sellers)) : null;
  const updatedAt = typeof o.updatedAt === "string" ? o.updatedAt : null;
  return { sellersWithCabinet: count, updatedAt };
}

async function fetchJson(url: string): Promise<PublicMetrics | null> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) return null;
  return parseMetrics(await res.json());
}

async function loadMetrics(): Promise<PublicMetrics | null> {
  if (LIVE_METRICS_URL) {
    const live = await fetchJson(LIVE_METRICS_URL);
    if (live?.sellersWithCabinet != null) return live;
  }
  return fetchJson(METRICS_JSON_URL);
}

export function LiveSellerCount({ className = "" }: { className?: string }) {
  const [count, setCount] = useState<number | null>(null);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;

    const tick = async () => {
      try {
        const data = await loadMetrics();
        if (!alive || !data) return;
        setCount(data.sellersWithCabinet);
        setUpdatedAt(data.updatedAt);
      } catch {
        /* keep last value */
      } finally {
        if (alive) setLoading(false);
      }
    };

    void tick();
    const id = window.setInterval(() => void tick(), REFRESH_MS);
    return () => {
      alive = false;
      window.clearInterval(id);
    };
  }, []);

  if (loading && count === null) {
    return (
      <p className={`text-small text-ink-muted ${className}`} aria-busy="true">
        <span className="inline-block h-4 w-48 animate-pulse rounded bg-surface-muted" />
      </p>
    );
  }

  if (count === null) {
    return (
      <p className={`text-small text-ink-muted ${className}`}>
        Счётчик подключённых кабинетов обновляется автоматически — цифра появится, как только
        синхронизация с ботом настроена.
      </p>
    );
  }

  if (count === 0) {
    return (
      <p className={`text-small text-ink-muted ${className}`}>
        Сервис только набирает аудиторию — подключите кабинет и будьте среди первых
        {updatedAt && <span className="text-ink-subtle"> · данные обновляются каждый час</span>}
      </p>
    );
  }

  const updatedLabel =
    updatedAt &&
    (() => {
      try {
        return new Intl.DateTimeFormat("ru-RU", {
          day: "numeric",
          month: "short",
          hour: "2-digit",
          minute: "2-digit",
          timeZone: "Europe/Minsk",
        }).format(new Date(updatedAt));
      } catch {
        return null;
      }
    })();

  return (
    <p className={`text-small text-ink-muted ${className}`}>
      Уже{" "}
      <span className="font-display font-semibold text-brand-800">{pluralSellers(count)}</span>{" "}
      подключили кабинет WB или Ozon и отвечают через бота
      {updatedLabel && (
        <span className="text-ink-subtle"> · обновлено {updatedLabel} (Минск)</span>
      )}
    </p>
  );
}
