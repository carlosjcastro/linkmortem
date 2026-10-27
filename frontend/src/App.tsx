import { useState } from "react";
import SiteFooter from "./components/SiteFooter";
import SiteHeader from "./components/SiteHeader";
import CaseFile from "./features/home/CaseFile";
import Hero from "./features/home/Hero";
import LostWeb from "./features/home/LostWeb";
import Procession from "./features/home/Procession";
import ScanResults from "./features/scan/ScanResults";
import { useScan } from "./features/scan/useScan";

export default function App() {
  const { state, start } = useScan();
  const [pulses, setPulses] = useState(0);
  const scanning = state.phase === "collecting" || state.phase === "checking";

  const scan = (target: string) => {
    setPulses((count) => count + 1);
    void start(target);
  };

  return (
    <>
      <SiteHeader />
      <main id="main">
        <Hero onScan={scan} pulses={pulses} scanning={scanning} />
        <ScanResults state={state} />
        <CaseFile />
        <Procession />
        <LostWeb />
      </main>
      <SiteFooter />
    </>
  );
}
