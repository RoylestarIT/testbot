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
    <>
      <Header />
      <main className={`min-h-[60vh] ${className}`}>{children}</main>
      <Footer />
    </>
  );
}
