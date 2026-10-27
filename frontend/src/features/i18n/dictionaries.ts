export type Language = "en" | "es";

type Step = { title: string; text: string };
type Finding = {
  term: string;
  value: string;
  tone: "dead" | "found" | "action";
};
type Fact = { figure: string; text: string; source: string; url: string };

export type Dictionary = {
  skip: string;
  motion: string;
  language: string;
  otherLanguage: string;
  heroTitle: string;
  heroLead: string;
  targetLabel: string;
  targetHint: string;
  targetPlaceholder: string;
  targetInvalid: string;
  scanAction: string;
  scanPending: string;
  caseTitle: string;
  caseText: string;
  caseExample: string;
  caseLink: string;
  caseFindings: Finding[];
  stepsTitle: string;
  stepsLead: string;
  steps: Step[];
  lostTitle: string;
  facts: Fact[];
  footerNote: string;
  footerSource: string;
  footerAuthor: string;
};

const ARCHIVE_STUDY =
  "https://blog.archive.org/2026/04/23/gone-but-not-forgotten-recovering-the-dead-web/";

export const dictionaries: Record<Language, Dictionary> = {
  en: {
    skip: "Skip to content",
    motion: "Animations",
    language: "Language",
    otherLanguage: "Español",
    heroTitle: "Every dead link is a ghost.",
    heroLead:
      "Linkmortem searches your website or your repository docs for links that lead nowhere, recovers what each lost page said from the Internet Archive and finds where it lives now.",
    targetLabel: "Website or GitHub repository",
    targetHint:
      "Only public pages are read, and nothing changes without your approval.",
    targetPlaceholder: "example.com or github.com/owner/repo",
    targetInvalid:
      "Enter a public web address, like example.com or github.com/owner/repo.",
    scanAction: "Find dead links",
    scanPending:
      "is ready to be searched. Scanning arrives in the next release.",
    caseTitle: "GeoCities went dark on October 26, 2009.",
    caseText:
      "Millions of personal pages disappeared overnight, and every link that pointed to them turned into a ghost. This is the kind of autopsy Linkmortem writes for each one.",
    caseExample: "Example autopsy",
    caseLink: "http://www.geocities.com/SiliconValley/",
    caseFindings: [
      {
        term: "Cause of death",
        value: "The host shut down and the address stopped serving pages.",
        tone: "dead",
      },
      {
        term: "Memory",
        value: "Archived copies survive in the Wayback Machine.",
        tone: "found",
      },
      {
        term: "Afterlife",
        value:
          "Community mirrors such as OoCities keep part of the content online.",
        tone: "found",
      },
      {
        term: "Rest",
        value:
          "Replace the link with its archived copy and note the original address.",
        tone: "action",
      },
    ],
    stepsTitle: "How a link is laid to rest",
    stepsLead:
      "Code checks every fact. Gemma only reads what code can't, like whether a page that answers is really alive.",
    steps: [
      {
        title: "Find",
        text: "Collects every link from the pages of a site or the Markdown files of a public repository.",
      },
      {
        title: "Diagnose",
        text: "Checks each link and spots pages that answer but are dead inside, like parked domains or error pages in disguise.",
      },
      {
        title: "Remember",
        text: "Recovers the last healthy copy of each lost page from the Wayback Machine.",
      },
      {
        title: "Reincarnate",
        text: "Looks for the content at a new address and confirms it is the same page, not a lookalike.",
      },
      {
        title: "Rest",
        text: "Proposes a replacement for each link, with the evidence behind it, ready to apply.",
      },
      {
        title: "Preserve",
        text: "Archives living links that were never saved, before they disappear too.",
      },
    ],
    lostTitle: "The web forgets faster than we think",
    facts: [
      {
        figure: "38%",
        text: "of the web pages that existed in 2013 were gone ten years later.",
        source: "Pew Research Center, 2024",
        url: ARCHIVE_STUDY,
      },
      {
        figure: "72%",
        text: "of the links in New York Times articles from 1998 no longer work.",
        source: "Zittrain and colleagues, 2021",
        url: ARCHIVE_STUDY,
      },
    ],
    footerNote:
      "Linkmortem reads public pages only and never edits anything on its own.",
    footerSource: "Source code under the MIT license",
    footerAuthor: "Built by Carlos José Castro Galante",
  },
  es: {
    skip: "Saltar al contenido",
    motion: "Animaciones",
    language: "Idioma",
    otherLanguage: "English",
    heroTitle: "Cada enlace muerto es un fantasma.",
    heroLead:
      "Linkmortem revisa tu sitio web o la documentación de tu repositorio en busca de enlaces que no llevan a ningún lado, recupera lo que decía cada página perdida desde el Internet Archive y encuentra dónde vive ahora.",
    targetLabel: "Sitio web o repositorio de GitHub",
    targetHint:
      "Solo se leen páginas públicas, y nada cambia sin tu aprobación.",
    targetPlaceholder: "ejemplo.com o github.com/usuario/repositorio",
    targetInvalid:
      "Ingresá una dirección web pública, como ejemplo.com o github.com/usuario/repositorio.",
    scanAction: "Buscar enlaces muertos",
    scanPending:
      "está lista para revisarse. El escaneo llega en la próxima versión.",
    caseTitle: "GeoCities se apagó el 26 de octubre de 2009.",
    caseText:
      "Millones de páginas personales desaparecieron de un día para el otro, y cada enlace que apuntaba a ellas se convirtió en un fantasma. Esta es la autopsia que Linkmortem escribe para cada uno.",
    caseExample: "Autopsia de ejemplo",
    caseLink: "http://www.geocities.com/SiliconValley/",
    caseFindings: [
      {
        term: "Causa de muerte",
        value: "El servicio cerró y la dirección dejó de mostrar páginas.",
        tone: "dead",
      },
      {
        term: "Memoria",
        value: "Quedan copias archivadas en el Wayback Machine.",
        tone: "found",
      },
      {
        term: "Más allá",
        value:
          "Espejos de la comunidad como OoCities mantienen parte del contenido en línea.",
        tone: "found",
      },
      {
        term: "Descanso",
        value:
          "Reemplazar el enlace por su copia archivada y dejar anotada la dirección original.",
        tone: "action",
      },
    ],
    stepsTitle: "Cómo descansa un enlace",
    stepsLead:
      "El código verifica cada dato. Gemma solo lee lo que el código no puede, como si una página que responde está viva de verdad.",
    steps: [
      {
        title: "Encontrar",
        text: "Reúne todos los enlaces de las páginas de un sitio o de los archivos Markdown de un repositorio público.",
      },
      {
        title: "Diagnosticar",
        text: "Revisa cada enlace y detecta páginas que responden pero están muertas por dentro, como dominios en venta o errores disfrazados.",
      },
      {
        title: "Recordar",
        text: "Recupera la última copia sana de cada página perdida desde el Wayback Machine.",
      },
      {
        title: "Reencarnar",
        text: "Busca el contenido en una dirección nueva y confirma que es la misma página, no una parecida.",
      },
      {
        title: "Descansar",
        text: "Propone un reemplazo para cada enlace, con la evidencia que lo respalda, listo para aplicar.",
      },
      {
        title: "Preservar",
        text: "Archiva los enlaces vivos que nunca se guardaron, antes de que también desaparezcan.",
      },
    ],
    lostTitle: "La web olvida más rápido de lo que creemos",
    facts: [
      {
        figure: "38%",
        text: "de las páginas web que existían en 2013 ya no estaban diez años después.",
        source: "Pew Research Center, 2024",
        url: ARCHIVE_STUDY,
      },
      {
        figure: "72%",
        text: "de los enlaces de los artículos del New York Times de 1998 ya no funcionan.",
        source: "Zittrain y colegas, 2021",
        url: ARCHIVE_STUDY,
      },
    ],
    footerNote:
      "Linkmortem solo lee páginas públicas y nunca edita nada por su cuenta.",
    footerSource: "Código fuente bajo licencia MIT",
    footerAuthor: "Hecho por Carlos José Castro Galante",
  },
};
