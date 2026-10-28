import { asset } from "./constants";

export type PublicMetrics = {
  sellersWithCabinet: number | null;
  telegramAccounts?: number | null;
  updatedAt: string | null;
};

export const METRICS_JSON_URL = asset("/metrics.json");

/** Прямой URL бота (опционально). Задаётся при сборке: NEXT_PUBLIC_LIVE_METRICS_URL */
export const LIVE_METRICS_URL = process.env.NEXT_PUBLIC_LIVE_METRICS_URL?.trim() || "";

export function pluralSellers(count: number): string {
  const n = Math.abs(Math.trunc(count));
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod100 >= 11 && mod100 <= 14) return `${n} селлеров`;
  if (mod10 === 1) return `${n} селлер`;
  if (mod10 >= 2 && mod10 <= 4) return `${n} селлера`;
  return `${n} селлеров`;
}
