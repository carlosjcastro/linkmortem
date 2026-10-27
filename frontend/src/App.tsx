import SiteFooter from "./components/SiteFooter";
import SiteHeader from "./components/SiteHeader";
import CaseFile from "./features/home/CaseFile";
import Hero from "./features/home/Hero";
import LostWeb from "./features/home/LostWeb";
import Procession from "./features/home/Procession";

export default function App() {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <Hero />
        <CaseFile />
        <Procession />
        <LostWeb />
      </main>
      <SiteFooter />
    </>
  );
}
