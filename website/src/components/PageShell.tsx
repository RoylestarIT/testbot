import { Header } from "./Header";
import { Footer } from "./Footer";

export function PageShell({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)]">
      <Header />
      <main className={`flex-1 ${className}`}>{children}</main>
      <Footer />
    </div>
  );
}
