import { clsx, type ClassValue } from "clsx";
import { extendTailwindMerge } from "tailwind-merge";

// Custom fontSize keys from tailwind.config.ts; without this `text-caption` would be
// treated as a color and could drop a real `text-*` color class.
const twMerge = extendTailwindMerge({
  extend: {
    classGroups: {
      "font-size": [{ text: ["display-lg", "display", "title", "body-lg", "body", "caption"] }],
    },
  },
});

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
