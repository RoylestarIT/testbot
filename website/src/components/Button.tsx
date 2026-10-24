import Link from "next/link";
import type { ReactNode } from "react";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "white";
export type ButtonSize = "md" | "lg";

const base =
  "group inline-flex items-center justify-center gap-2 rounded-full font-semibold tracking-[-0.01em] transition-all duration-200 ease-smooth will-change-transform active:translate-y-0 active:scale-[0.98] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500";

const sizes: Record<ButtonSize, string> = {
  md: "h-11 px-5 text-small",
  lg: "h-[3.25rem] px-7 text-body",
};

const variants: Record<ButtonVariant, string> = {
  primary:
    "bg-brand-700 text-white shadow-button hover:-translate-y-0.5 hover:bg-brand-800 hover:shadow-button-hover",
  secondary:
    "border border-line-strong bg-white text-ink shadow-xs hover:-translate-y-0.5 hover:border-brand-300 hover:text-brand-800 hover:shadow-card",
  ghost: "text-brand-700 hover:bg-brand-50",
  white:
    "bg-white text-brand-900 shadow-button hover:-translate-y-0.5 hover:bg-brand-50 hover:shadow-button-hover",
};

export function buttonClass(variant: ButtonVariant = "primary", size: ButtonSize = "md") {
  return `${base} ${sizes[size]} ${variants[variant]}`;
}

export function Button({
  href,
  children,
  variant = "primary",
  size = "md",
  external = false,
  className = "",
  leading,
  trailing,
}: {
  href: string;
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  external?: boolean;
  className?: string;
  leading?: ReactNode;
  trailing?: ReactNode;
}) {
  const content = (
    <>
      {leading}
      <span>{children}</span>
      {trailing && (
        <span className="transition-transform duration-200 ease-smooth group-hover:translate-x-0.5">
          {trailing}
        </span>
      )}
    </>
  );
  const cls = `${buttonClass(variant, size)} ${className}`;

  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={cls}>
        {content}
      </a>
    );
  }
  return (
    <Link href={href} className={cls}>
      {content}
    </Link>
  );
}
