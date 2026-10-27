import { useState } from "react";
import HauntingCanvas from "../haunting/HauntingCanvas";
import { useTranslation } from "../i18n/useTranslation";
import ScanForm from "../scan/ScanForm";

export default function Hero() {
  const { t } = useTranslation();
  const [target, setTarget] = useState<string | null>(null);
  const [pulses, setPulses] = useState(0);

  const scan = (address: string) => {
    setTarget(address);
    setPulses((count) => count + 1);
  };

  return (
    <section
      aria-labelledby="heroTitle"
      className="relative isolate lg:min-h-[calc(100svh_+_1rem)]"
    >
      <div className="fade-bottom pointer-events-none relative h-[46svh] min-h-80 lg:absolute lg:inset-0 lg:h-auto">
        <HauntingCanvas pulseSignal={pulses} />
      </div>
      <div className="relative mx-auto w-full max-w-7xl px-5 pb-20 sm:px-10 lg:pt-[12svh]">
        <h1
          id="heroTitle"
          className="spectral-type max-w-[11ch] font-display text-[clamp(3.1rem,8.4vw,7.6rem)] leading-[0.95] tracking-[-0.02em] text-bone"
        >
          {t.heroTitle}
        </h1>
        <p className="mt-8 max-w-[38rem] text-[1.2rem] leading-[1.65] text-dusk">
          {t.heroLead}
        </p>
        <ScanForm onScan={scan} />
        <p aria-live="polite" className="mt-5 min-h-6 max-w-xl text-spectral">
          {target ? `${target} ${t.scanPending}` : ""}
        </p>
      </div>
    </section>
  );
}
