import { useEffect, useState } from "react";
import SiteFooter from "./components/SiteFooter";
import SiteHeader from "./components/SiteHeader";
import CaseFile from "./features/home/CaseFile";
import Hero from "./features/home/Hero";
import LostWeb from "./features/home/LostWeb";
import Procession from "./features/home/Procession";
import ScanResults from "./features/scan/ScanResults";
import { sharedScanId } from "./features/scan/savedScan";
import { useScan } from "./features/scan/useScan";

export default function App() {
  const { state, start, load } = useScan();
  const [pulses, setPulses] = useState(0);
  const scanning = state.phase === "collecting" || state.phase === "checking";

  useEffect(() => {
    const id = sharedScanId(window.location.pathname);
    if (id) void load(id);
  }, [load]);

  useEffect(() => {
    if (
      state.shareId &&
      sharedScanId(window.location.pathname) !== state.shareId
    ) {
      window.history.replaceState(null, "", `/r/${state.shareId}`);
    }
  }, [state.shareId]);

  const scan = (target: string) => {
    setPulses((count) => count + 1);
    window.history.replaceState(null, "", "/");
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
