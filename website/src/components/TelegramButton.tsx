import { BOT_URL, BOT_URL_SITE } from "@/content/constants";
import { Button, type ButtonSize, type ButtonVariant } from "./Button";
import { TelegramIcon } from "./TelegramIcon";

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
      leading={
        <TelegramIcon className="h-[1.125rem] w-[1.125rem] shrink-0 transition-transform duration-200 ease-smooth group-hover:translate-x-0.5 group-hover:-translate-y-px" />
      }
    >
      {children}
    </Button>
  );
}
