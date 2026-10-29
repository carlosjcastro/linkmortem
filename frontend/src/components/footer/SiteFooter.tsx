import FooterEpitaph from "./FooterEpitaph";
import FooterFineprint from "./FooterFineprint";
import FooterNav from "./FooterNav";
import GraveyardHorizon from "./GraveyardHorizon";

export default function SiteFooter() {
  return (
    <footer className="mt-24 text-dusk">
      <GraveyardHorizon />
      <div className="bg-grave">
        <div className="mx-auto grid w-full max-w-7xl gap-14 px-5 pb-14 pt-12 sm:px-10 lg:grid-cols-[1fr_1.4fr] lg:gap-16">
          <FooterEpitaph />
          <FooterNav />
        </div>
        <FooterFineprint />
      </div>
    </footer>
  );
}
