export type Language = "en" | "es";

type Step = { title: string; text: string };
type Finding = { term: string; value: string; tone: "dead" | "found" | "action" };
type Fact = { figure: string; text: string; source: string; url: string };
type CauseName = import("../scan/scanTypes").Cause;

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
  scanCollecting: string;
  scanChecked: (checked: number, total: number) => string;
  resultsTitle: string;
  resultsDone: (ghosts: number) => string;
  ghostsTitle: string;
  unknownTitle: string;
  aliveTitle: string;
  foundOn: string;
  scanRemembering: (remembered: number, ghosts: number) => string;
  scanReincarnating: (sought: number, total: number) => string;
  memorySearching: string;
  memoryFound: (date: string) => string;
  memoryMissing: string;
  memoryUnavailable: string;
  afterlifeSearching: string;
  afterlifeSame: string;
  afterlifeSuccessor: string;
  afterlifeNone: string;
  afterlifeUnavailable: string;
  afterlifeSkipped: string;
  afterlifeFromGraveyard: string;
  shareTitle: string;
  shareHint: string;
  shareCopy: string;
  shareCopied: string;
  causes: Record<CauseName, string>;
  scanErrors: Record<string, string>;
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

const ARCHIVE_STUDY = "https://blog.archive.org/2026/04/23/gone-but-not-forgotten-recovering-the-dead-web/";

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
    targetHint: "Only public pages are read, and nothing changes without your approval.",
    targetPlaceholder: "example.com or github.com/owner/repo",
    targetInvalid: "Enter a public web address, like example.com or github.com/owner/repo.",
    scanAction: "Find dead links",
    scanCollecting: "Gathering every link from the pages",
    scanChecked: (checked, total) => `Checked ${checked} of ${total} links`,
    resultsTitle: "Searching for ghosts",
    resultsDone: (ghosts) => (ghosts === 0 ? "No ghosts here. Every link still leads somewhere." : ghosts === 1 ? "One link has become a ghost." : `${ghosts} links have become ghosts.`),
    ghostsTitle: "Ghosts",
    unknownTitle: "Could not confirm",
    aliveTitle: "Still alive",
    foundOn: "Found on",
    scanRemembering: (remembered, ghosts) => `Searching the Wayback Machine for ${ghosts === 1 ? "the lost page" : "the lost pages"}, ${remembered} of ${ghosts}`,
    scanReincarnating: (sought, total) => `Looking for where the lost pages live now, ${sought} of ${total}`,
    memorySearching: "Searching the Wayback Machine for its last healthy copy",
    memoryFound: (date) => `Last healthy copy, ${date}`,
    memoryMissing: "The Wayback Machine never saved a healthy copy of this page.",
    memoryUnavailable: "The Wayback Machine didn't answer. Try again in a few minutes.",
    afterlifeSearching: "Looking for where this page lives now",
    afterlifeSame: "Reincarnated at a new address",
    afterlifeSuccessor: "Lives on in a newer version",
    afterlifeNone: "No new home found. The archived copy is the best replacement.",
    afterlifeUnavailable: "The search for a new home didn't answer. Try again later.",
    afterlifeSkipped: "This scan reached its search limit, so this page wasn't looked up.",
    afterlifeFromGraveyard: "Found in Linkmortem's graveyard of resolved links, without a new web search.",
    shareTitle: "Share this autopsy",
    shareHint: "Anyone with the link can read these results for 30 days.",
    shareCopy: "Copy link",
    shareCopied: "Link copied",
    causes: {
      alive: "Alive",
      unreadable: "Alive, though its content loads with scripts",
      not_found: "The page no longer exists",
      gone: "The page was removed on purpose",
      dns_failure: "The domain no longer exists",
      parked_domain: "The domain is parked or for sale",
      error_page: "An error page in disguise",
      placeholder: "An empty or unfinished page",
      unrelated_redirect: "Sends readers somewhere unrelated",
      server_error: "The server failed to answer",
      unreachable: "Could not reach the server",
      timeout: "The server took too long",
      restricted: "Hidden behind a login or bot check",
      blocked: "Private address, not checked",
      unclassified: "Gemma could not decide",
    },
    scanErrors: {
      invalid_target: "Enter a public web address that starts with http or https.",
      repository_not_found: "That repository doesn't exist or isn't public.",
      source_unreachable: "The source didn't answer. Try again in a few minutes.",
      github_rate_limited: "GitHub's hourly limit for this server ran out. Try again in an hour, or set GITHUB_TOKEN in the backend.",
      scan_not_found: "That autopsy doesn't exist or has expired.",
      nothing_found: "No links were found at that address.",
      too_many_scans: "You reached the scan limit. Try again in a few minutes.",
      busy: "Linkmortem is busy with other scans. Try again in a minute.",
      unavailable: "The scan stopped unexpectedly. Check your connection and try again.",
    },
    caseTitle: "GeoCities went dark on October 26, 2009.",
    caseText:
      "Millions of personal pages disappeared overnight, and every link that pointed to them turned into a ghost. This is the kind of autopsy Linkmortem writes for each one.",
    caseExample: "Example autopsy",
    caseLink: "http://www.geocities.com/SiliconValley/",
    caseFindings: [
      { term: "Cause of death", value: "The host shut down and the address stopped serving pages.", tone: "dead" },
      { term: "Memory", value: "Archived copies survive in the Wayback Machine.", tone: "found" },
      { term: "Afterlife", value: "Community mirrors such as OoCities keep part of the content online.", tone: "found" },
      { term: "Rest", value: "Replace the link with its archived copy and note the original address.", tone: "action" },
    ],
    stepsTitle: "How a link is laid to rest",
    stepsLead: "Code checks every fact. Gemma only reads what code can't, like whether a page that answers is really alive.",
    steps: [
      { title: "Find", text: "Collects every link from the pages of a site or the Markdown files of a public repository." },
      { title: "Diagnose", text: "Checks each link and spots pages that answer but are dead inside, like parked domains or error pages in disguise." },
      { title: "Remember", text: "Recovers the last healthy copy of each lost page from the Wayback Machine." },
      { title: "Reincarnate", text: "Looks for the content at a new address and confirms it is the same page, not a lookalike." },
      { title: "Rest", text: "Proposes a replacement for each link, with the evidence behind it, ready to apply." },
      { title: "Preserve", text: "Archives living links that were never saved, before they disappear too." },
    ],
    lostTitle: "The web forgets faster than we think",
    facts: [
      { figure: "38%", text: "of the web pages that existed in 2013 were gone ten years later.", source: "Pew Research Center, 2024", url: ARCHIVE_STUDY },
      { figure: "72%", text: "of the links in New York Times articles from 1998 no longer work.", source: "Zittrain and colleagues, 2021", url: ARCHIVE_STUDY },
    ],
    footerNote: "Linkmortem reads public pages only and never edits anything on its own.",
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
    targetHint: "Solo se leen páginas públicas, y nada cambia sin tu aprobación.",
    targetPlaceholder: "ejemplo.com o github.com/usuario/repositorio",
    targetInvalid: "Ingresá una dirección web pública, como ejemplo.com o github.com/usuario/repositorio.",
    scanAction: "Buscar enlaces muertos",
    scanCollecting: "Reuniendo todos los enlaces de las páginas",
    scanChecked: (checked, total) => `Revisados ${checked} de ${total} enlaces`,
    resultsTitle: "Buscando fantasmas",
    resultsDone: (ghosts) => (ghosts === 0 ? "No hay fantasmas. Todos los enlaces siguen llevando a algún lado." : ghosts === 1 ? "Un enlace se convirtió en fantasma." : `${ghosts} enlaces se convirtieron en fantasmas.`),
    ghostsTitle: "Fantasmas",
    unknownTitle: "Sin confirmar",
    aliveTitle: "Siguen vivos",
    foundOn: "Encontrado en",
    scanRemembering: (remembered, ghosts) => `Buscando ${ghosts === 1 ? "la página perdida" : "las páginas perdidas"} en el Wayback Machine, ${remembered} de ${ghosts}`,
    scanReincarnating: (sought, total) => `Buscando dónde viven hoy las páginas perdidas, ${sought} de ${total}`,
    memorySearching: "Buscando su última copia sana en el Wayback Machine",
    memoryFound: (date) => `Última copia sana, ${date}`,
    memoryMissing: "El Wayback Machine nunca guardó una copia sana de esta página.",
    memoryUnavailable: "El Wayback Machine no respondió. Probá de nuevo en unos minutos.",
    afterlifeSearching: "Buscando dónde vive hoy esta página",
    afterlifeSame: "Reencarnó en una nueva dirección",
    afterlifeSuccessor: "Sigue viva en una versión más nueva",
    afterlifeNone: "No encontramos un nuevo hogar. La copia archivada es el mejor reemplazo.",
    afterlifeUnavailable: "La búsqueda de un nuevo hogar no respondió. Probá más tarde.",
    afterlifeSkipped: "Este escaneo llegó a su límite de búsquedas, así que esta página no se buscó.",
    afterlifeFromGraveyard: "Encontrada en el cementerio de enlaces resueltos de Linkmortem, sin una nueva búsqueda web.",
    shareTitle: "Compartí esta autopsia",
    shareHint: "Cualquiera con el enlace puede leer estos resultados durante 30 días.",
    shareCopy: "Copiar enlace",
    shareCopied: "Enlace copiado",
    causes: {
      alive: "Vivo",
      unreadable: "Vivo, aunque su contenido carga con scripts",
      not_found: "La página ya no existe",
      gone: "La página fue eliminada a propósito",
      dns_failure: "El dominio ya no existe",
      parked_domain: "El dominio está estacionado o en venta",
      error_page: "Una página de error disfrazada",
      placeholder: "Una página vacía o sin terminar",
      unrelated_redirect: "Lleva a un contenido sin relación",
      server_error: "El servidor no pudo responder",
      unreachable: "No se pudo llegar al servidor",
      timeout: "El servidor tardó demasiado",
      restricted: "Oculta tras un inicio de sesión o un control de bots",
      blocked: "Dirección privada, no se revisó",
      unclassified: "Gemma no pudo decidir",
    },
    scanErrors: {
      invalid_target: "Ingresá una dirección web pública que empiece con http o https.",
      repository_not_found: "Ese repositorio no existe o no es público.",
      source_unreachable: "La fuente no respondió. Probá de nuevo en unos minutos.",
      github_rate_limited: "Se agotó el límite por hora de GitHub para este servidor. Probá en una hora o configurá GITHUB_TOKEN en el backend.",
      scan_not_found: "Esa autopsia no existe o ya venció.",
      nothing_found: "No se encontraron enlaces en esa dirección.",
      too_many_scans: "Llegaste al límite de escaneos. Probá de nuevo en unos minutos.",
      busy: "Linkmortem está ocupado con otros escaneos. Probá de nuevo en un minuto.",
      unavailable: "El escaneo se cortó inesperadamente. Revisá tu conexión y probá de nuevo.",
    },
    caseTitle: "GeoCities se apagó el 26 de octubre de 2009.",
    caseText:
      "Millones de páginas personales desaparecieron de un día para el otro, y cada enlace que apuntaba a ellas se convirtió en un fantasma. Esta es la autopsia que Linkmortem escribe para cada uno.",
    caseExample: "Autopsia de ejemplo",
    caseLink: "http://www.geocities.com/SiliconValley/",
    caseFindings: [
      { term: "Causa de muerte", value: "El servicio cerró y la dirección dejó de mostrar páginas.", tone: "dead" },
      { term: "Memoria", value: "Quedan copias archivadas en el Wayback Machine.", tone: "found" },
      { term: "Más allá", value: "Espejos de la comunidad como OoCities mantienen parte del contenido en línea.", tone: "found" },
      { term: "Descanso", value: "Reemplazar el enlace por su copia archivada y dejar anotada la dirección original.", tone: "action" },
    ],
    stepsTitle: "Cómo descansa un enlace",
    stepsLead: "El código verifica cada dato. Gemma solo lee lo que el código no puede, como si una página que responde está viva de verdad.",
    steps: [
      { title: "Encontrar", text: "Reúne todos los enlaces de las páginas de un sitio o de los archivos Markdown de un repositorio público." },
      { title: "Diagnosticar", text: "Revisa cada enlace y detecta páginas que responden pero están muertas por dentro, como dominios en venta o errores disfrazados." },
      { title: "Recordar", text: "Recupera la última copia sana de cada página perdida desde el Wayback Machine." },
      { title: "Reencarnar", text: "Busca el contenido en una dirección nueva y confirma que es la misma página, no una parecida." },
      { title: "Descansar", text: "Propone un reemplazo para cada enlace, con la evidencia que lo respalda, listo para aplicar." },
      { title: "Preservar", text: "Archiva los enlaces vivos que nunca se guardaron, antes de que también desaparezcan." },
    ],
    lostTitle: "La web olvida más rápido de lo que creemos",
    facts: [
      { figure: "38%", text: "de las páginas web que existían en 2013 ya no estaban diez años después.", source: "Pew Research Center, 2024", url: ARCHIVE_STUDY },
      { figure: "72%", text: "de los enlaces de los artículos del New York Times de 1998 ya no funcionan.", source: "Zittrain y colegas, 2021", url: ARCHIVE_STUDY },
    ],
    footerNote: "Linkmortem solo lee páginas públicas y nunca edita nada por su cuenta.",
    footerSource: "Código fuente bajo licencia MIT",
    footerAuthor: "Hecho por Carlos José Castro Galante",
  },
};
