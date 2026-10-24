import { BOT_URL, BOT_URL_SITE } from "@/content/constants";
import { Button, type ButtonSize, type ButtonVariant } from "./Button";

type Props = {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  className?: string;
  trackSite?: boolean;
};

export function TelegramButton({
  children,
  variant = "primary",
  size = "md",
  className = "",
  trackSite = false,
}: Props) {
  return (
    <Button
      href={trackSite ? BOT_URL_SITE : BOT_URL}
      external
      variant={variant}
      size={size}
      className={className}
      leading={<TelegramIcon />}
    >
      {children}
    </Button>
  );
}

function TelegramIcon() {
  return (
    <svg
      aria-hidden
      className="h-[1.125rem] w-[1.125rem] shrink-0 transition-transform duration-200 ease-smooth group-hover:-rotate-6"
      viewBox="0 0 24 24"
      fill="currentColor"
    >
      <path d="M9.78 18.65l.28-4.23 7.68-6.92c.34-.31-.07-.46-.52-.19L7.74 13.3 3.64 12c-.88-.25-.88-1.08.2-1.6l15.57-6.01c.73-.33 1.43.18 1.15 1.3l-2.65 12.42c-.19.91-.74 1.13-1.5.71L12.6 16.3l-1.99 1.93c-.23.23-.42.42-.83.42z" />
    </svg>
  );
}
