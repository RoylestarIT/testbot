import { Header } from "./Header";
import { Footer } from "./Footer";
import { MobileCtaBar } from "./MobileCtaBar";

export function PageShell({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-full focus:bg-brand-700 focus:px-5 focus:py-3 focus:text-small focus:font-semibold focus:text-white"
      >
        Перейти к содержимому
      </a>
      <Header />
      <main id="main" className={`flex-1 ${className}`}>
        {children}
      </main>
      <Footer />
      <MobileCtaBar />
    </div>
  );
}
