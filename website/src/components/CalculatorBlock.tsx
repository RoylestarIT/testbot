import { SavingsCalculator } from "./SavingsCalculator";
import { CalculatorMicroFaq } from "./CalculatorMicroFaq";

/** Калькулятор + микро-FAQ; якорь `#calculator` для CTA с внутренних страниц. */
export function CalculatorBlock({ className = "" }: { className?: string }) {
  return (
    <div id="calculator" className={`scroll-mt-28 ${className}`}>
      <SavingsCalculator />
      <CalculatorMicroFaq />
    </div>
  );
}
