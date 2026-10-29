export type Language = "en" | "es";

type Step = { title: string; text: string };
type Finding = {
  term: string;
  value: string;
  tone: "dead" | "found" | "action";
};
type Fact = { figure: string; text: string; source: string; url: string };
type CauseName = import("../scan/scanTypes").Cause;
type FooterGroupKey =
  import("../../components/footer/footerLinks").FooterGroupKey;
type FooterLinkKey =
  import("../../components/footer/footerLinks").FooterLinkKey;

export type Dictionary = {
  skip: string;
  motion: string;
  language: string;
  nav: {
    label: string;
    howItWorks: string;
    action: string;
    repository: string;
  };
  heroTitle: string;
  heroLead: string;
  targetLabel: string;
  targetHint: string;
  targetPlaceholder: string;
  targetInvalid: string;
  scanAction: string;
  tryExample: string;
  scanCollecting: string;
  scanChecked: (checked: number, total: number) => string;
  resultsTitle: string;
  resultsDone: (ghosts: number) => string;
  ghostsTitle: string;
  unknownTitle: string;
  aliveTitle: string;
  foundOn: string;
  moreSources: (count: number) => string;
  coverageLinks: (checked: number, found: number) => string;
  coverageSources: (
    read: number,
    available: number,
    repository: boolean,
  ) => string;
  scanRemembering: (remembered: number, ghosts: number) => string;
  scanReincarnating: (sought: number, total: number) => string;
  memorySearching: string;
  memoryFound: (date: string) => string;
  memoryMissing: string;
  memoryUnavailable: string;
  afterlifeSearching: string;
  afterlifeSame: string;
  afterlifeSection: string;
  afterlifeSuccessor: string;
  afterlifeNone: string;
  afterlifeUnavailable: string;
  afterlifeSkipped: string;
  afterlifeBudgetSpent: string;
  afterlifeFromGraveyard: string;
  afterlifeAnnounced: string;
  shareTitle: string;
  watchTitle: string;
  watchText: string;
  watchCopy: string;
  watchCopied: string;
  watchShow: string;
  watchSetup: string;
  shareHint: string;
  shareCopy: string;
  shareCopied: string;
  restTitle: string;
  restText: (count: number) => string;
  restDownload: string;
  restApply: string;
  preserveTitle: string;
  preserveText: (count: number) => string;
  preserveAction: string;
  preserveProgress: (sent: number, total: number) => string;
  preserveDone: (queued: number) => string;
  preserveQueued: string;
  preserveFailed: string;
  preserveRecent: string;
  preserveWaiting: string;
  modelMissing: (count: number) => string;
  houseTitle: string;
  houseLegend: Record<"alive" | "ghost" | "unknown", string>;
  houseHint: string;
  houseShowing: (shown: number, total: number) => string;
  tally: Record<"ghost" | "unknown" | "alive", string>;
  nextTitle: string;
  rowCause: string;
  rowMemory: string;
  rowAfterlife: string;
  unknownHint: string;
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
  footer: {
    memoriam: string;
    epitaph: string;
    note: string;
    navigation: string;
    groups: Record<FooterGroupKey, string>;
    links: Record<FooterLinkKey, string>;
    rights: string;
    challenge: string;
    disclaimer: string;
  };
};

const ARCHIVE_STUDY =
  "https://blog.archive.org/2026/04/23/gone-but-not-forgotten-recovering-the-dead-web/";

export const dictionaries: Record<Language, Dictionary> = {
  en: {
    skip: "Skip to content",
    motion: "Animations",
    language: "Language",
    nav: {
      label: "Main",
      howItWorks: "How it works",
      action: "GitHub Action",
      repository: "Source code on GitHub",
    },
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
    tryExample: "Or try it on the demo repository",
    scanCollecting: "Gathering the links to check",
    scanChecked: (checked, total) => `Checked ${checked} of ${total} links`,
    resultsTitle: "Searching for ghosts",
    resultsDone: (ghosts) =>
      ghosts === 0
        ? "No ghosts here. Every link still leads somewhere."
        : ghosts === 1
          ? "One link has become a ghost."
          : `${ghosts} links have become ghosts.`,
    ghostsTitle: "Ghosts",
    unknownTitle: "Could not confirm",
    aliveTitle: "Still alive",
    foundOn: "Found in",
    moreSources: (count) => `and ${count} more`,
    coverageLinks: (checked, found) =>
      `Linkmortem checked the first ${checked} of the ${found} links it found.`,
    coverageSources: (read, available, repository) =>
      `It read ${read} of the ${available} ${repository ? "Markdown files" : "pages"} it could reach.`,
    scanRemembering: (remembered, ghosts) =>
      `Searching the Wayback Machine for ${ghosts === 1 ? "the lost page" : "the lost pages"}, ${remembered} of ${ghosts}`,
    scanReincarnating: (sought, total) =>
      `Looking for where the lost pages live now, ${sought} of ${total}`,
    memorySearching: "Searching the Wayback Machine for its last healthy copy",
    memoryFound: (date) => `Last healthy copy, ${date}`,
    memoryMissing:
      "The Wayback Machine never saved a healthy copy of this page.",
    memoryUnavailable:
      "The Wayback Machine didn't answer. Try again in a few minutes.",
    afterlifeSearching: "Looking for where this page lives now",
    afterlifeSame: "Reincarnated at a new address",
    afterlifeSection: "Closest section in the same document",
    afterlifeSuccessor: "Lives on in a newer version",
    afterlifeNone:
      "No new home found. The archived copy is the best replacement.",
    afterlifeUnavailable:
      "The search for a new home didn't answer. Try again later.",
    afterlifeSkipped:
      "This scan reached its search limit, so this page wasn't looked up.",
    afterlifeBudgetSpent:
      "Linkmortem used up its web searches for today, so this page wasn't looked up. Its archived copy still works as a replacement.",
    afterlifeAnnounced:
      "The archived page itself announced this new address, and Linkmortem checked that it's alive.",
    afterlifeFromGraveyard:
      "Found in Linkmortem's graveyard of resolved links, without a new web search.",
    shareTitle: "Share this autopsy",
    watchTitle: "Keep watching this repository",
    watchText:
      "Add the Linkmortem Action and it scans your Markdown every Monday, keeps one issue up to date and opens one pull request with the replacements it can prove. It never merges on its own.",
    watchCopy: "Copy the workflow",
    watchCopied: "Copied",
    watchShow: "Show the workflow",
    watchSetup:
      "Save it as .github/workflows/linkmortem.yml, add the secrets you have and allow GitHub Actions to create pull requests in Settings, Actions, General.",
    shareHint: "Anyone with the link can read these results for 30 days.",
    shareCopy: "Copy link",
    shareCopied: "Link copied",
    restTitle: "Lay these links to rest",
    restText: (count) =>
      `A patch replaces ${count === 1 ? "1 dead link" : `${count} dead links`} with ${count === 1 ? "its" : "their"} new home or last healthy copy. Review it before applying.`,
    restDownload: "Download patch",
    restApply: "Apply it from your repository with",
    preserveTitle: "Preserve the living",
    preserveText: (count) =>
      `Ask the Internet Archive to save up to ${count} living ${count === 1 ? "link that wasn't" : "links that weren't"} saved this month, before ${count === 1 ? "it becomes a ghost" : "they become ghosts"} too.`,
    preserveAction: "Preserve living links",
    preserveProgress: (sent, total) =>
      `Sending pages to the Internet Archive, ${sent} of ${total}`,
    preserveDone: (safe) =>
      `${safe === 1 ? "1 page is" : `${safe} pages are`} safe in the Internet Archive or being saved now.`,
    preserveQueued: "Saving",
    preserveFailed: "Not saved",
    preserveRecent: "Already saved recently",
    preserveWaiting:
      "The Internet Archive is busy with these pages. Waiting a minute before the next one.",
    houseTitle:
      "The windows light up in proportion to your links, and every dead link rests in a grave.",
    houseLegend: {
      alive: "Lit, alive",
      unknown: "Flickering, couldn't confirm",
      ghost: "Dark window and a grave, dead",
    },
    houseHint: "Select a ghost to read its autopsy.",
    houseShowing: (shown, total) =>
      `The yard shows ${shown} of ${total} graves.`,
    tally: { ghost: "dead", unknown: "couldn't confirm", alive: "still alive" },
    nextTitle: "What you can do now",
    rowCause: "Cause of death",
    rowMemory: "Memory",
    rowAfterlife: "Afterlife",
    unknownHint:
      "These links answered in a way Linkmortem can't prove dead or alive. Open them yourself before changing anything.",
    modelMissing: (count) => {
      const pages =
        count === 1
          ? "1 page that looked suspicious stays"
          : `${count} pages that looked suspicious stay`;
      return `Gemma wasn't available during this scan, so ${pages} unconfirmed. Every other check still ran. Try again in a few minutes.`;
    },
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
      model_unavailable: "Gemma wasn't available to read it",
      missing_section: "The section no longer exists",
    },
    scanErrors: {
      invalid_target:
        "Enter a public web address that starts with http or https.",
      repository_not_found: "That repository doesn't exist or isn't public.",
      source_unreachable:
        "The source didn't answer. Try again in a few minutes.",
      github_rate_limited:
        "GitHub's hourly limit for this server ran out. Try again in an hour, or set GITHUB_TOKEN in the backend.",
      scan_not_found: "That autopsy doesn't exist or has expired.",
      preserve_unavailable: "Preserving pages isn't configured on this server.",
      already_preserved:
        "The living links of this autopsy were already sent to the archive.",
      nothing_found: "No links were found at that address.",
      too_many_scans: "You reached the scan limit. Try again in a few minutes.",
      busy: "Linkmortem is busy with other scans. Try again in a minute.",
      unavailable:
        "The scan stopped unexpectedly. Check your connection and try again.",
    },
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
        text: "Collects up to 150 links from the pages of a site or the Markdown files of a public repository, and says so when there were more.",
      },
      {
        title: "Diagnose",
        text: "Checks each link, down to the section it points to, and spots pages that answer but are dead inside, like parked domains or error pages in disguise.",
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
        text: "Writes a patch with the replacements it can prove and the evidence behind each one. The GitHub Action turns it into a pull request.",
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
    footer: {
      memoriam: "In memoriam",
      epitaph:
        "Here lie the links that led nowhere. May they rest, and may their pages be remembered.",
      note: "Linkmortem reads public pages only and never edits anything on its own.",
      navigation: "Footer",
      groups: {
        autopsy: "The autopsy",
        project: "The project",
        credits: "Kept alive by",
      },
      links: {
        scan: "Find dead links",
        action: "GitHub Action",
        actionDemo: "Action demo",
        source: "Source code",
        contributing: "Contributing",
        security: "Report a vulnerability",
        license: "MIT license",
        wayback: "Internet Archive's Wayback Machine",
        gemma: "Gemma, an open model by Google",
      },
      rights: "Code under the MIT license. Built for the",
      challenge: "DEV Hacktoberfest Open Source AI Challenge",
      disclaimer:
        "Results are automated and can be wrong, so review every replacement before you use it. Archived copies belong to the Internet Archive and to their original authors. Linkmortem isn't affiliated with the Internet Archive or Google.",
    },
  },
  es: {
    skip: "Saltar al contenido",
    motion: "Animaciones",
    language: "Idioma",
    nav: {
      label: "Principal",
      howItWorks: "Cómo funciona",
      action: "Action de GitHub",
      repository: "Código fuente en GitHub",
    },
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
    tryExample: "O probalo con el repositorio de demostración",
    scanCollecting: "Reuniendo los enlaces para revisar",
    scanChecked: (checked, total) => `Revisados ${checked} de ${total} enlaces`,
    resultsTitle: "Buscando fantasmas",
    resultsDone: (ghosts) =>
      ghosts === 0
        ? "No hay fantasmas. Todos los enlaces siguen llevando a algún lado."
        : ghosts === 1
          ? "Un enlace se convirtió en fantasma."
          : `${ghosts} enlaces se convirtieron en fantasmas.`,
    ghostsTitle: "Fantasmas",
    unknownTitle: "Sin confirmar",
    aliveTitle: "Siguen vivos",
    foundOn: "Encontrado en",
    moreSources: (count) => `y ${count} más`,
    coverageLinks: (checked, found) =>
      `Linkmortem revisó los primeros ${checked} de los ${found} enlaces que encontró.`,
    coverageSources: (read, available, repository) =>
      `Leyó ${read} de ${repository ? `los ${available} archivos Markdown` : `las ${available} páginas`} que pudo alcanzar.`,
    scanRemembering: (remembered, ghosts) =>
      `Buscando ${ghosts === 1 ? "la página perdida" : "las páginas perdidas"} en el Wayback Machine, ${remembered} de ${ghosts}`,
    scanReincarnating: (sought, total) =>
      `Buscando dónde viven hoy las páginas perdidas, ${sought} de ${total}`,
    memorySearching: "Buscando su última copia sana en el Wayback Machine",
    memoryFound: (date) => `Última copia sana, ${date}`,
    memoryMissing:
      "El Wayback Machine nunca guardó una copia sana de esta página.",
    memoryUnavailable:
      "El Wayback Machine no respondió. Probá de nuevo en unos minutos.",
    afterlifeSearching: "Buscando dónde vive hoy esta página",
    afterlifeSame: "Reencarnó en una nueva dirección",
    afterlifeSection: "La sección más parecida del mismo documento",
    afterlifeSuccessor: "Sigue viva en una versión más nueva",
    afterlifeNone:
      "No encontramos un nuevo hogar. La copia archivada es el mejor reemplazo.",
    afterlifeUnavailable:
      "La búsqueda de un nuevo hogar no respondió. Probá más tarde.",
    afterlifeSkipped:
      "Este escaneo llegó a su límite de búsquedas, así que esta página no se buscó.",
    afterlifeBudgetSpent:
      "Linkmortem agotó sus búsquedas web por hoy, así que esta página no se buscó. Su copia archivada sigue sirviendo como reemplazo.",
    afterlifeAnnounced:
      "La propia página archivada anunciaba esta dirección nueva, y Linkmortem comprobó que está viva.",
    afterlifeFromGraveyard:
      "Encontrada en el cementerio de enlaces resueltos de Linkmortem, sin una nueva búsqueda web.",
    shareTitle: "Compartí esta autopsia",
    watchTitle: "Seguí vigilando este repositorio",
    watchText:
      "Sumá la Action de Linkmortem y revisa tu Markdown cada lunes, mantiene un issue al día y abre un pull request con los reemplazos que puede probar. Nunca mergea por su cuenta.",
    watchCopy: "Copiar el workflow",
    watchCopied: "Copiado",
    watchShow: "Ver el workflow",
    watchSetup:
      "Guardalo como .github/workflows/linkmortem.yml, agregá los secretos que tengas y permití que GitHub Actions cree pull requests en Settings, Actions, General.",
    shareHint:
      "Cualquiera con el enlace puede leer estos resultados durante 30 días.",
    shareCopy: "Copiar enlace",
    shareCopied: "Enlace copiado",
    restTitle: "Dales descanso a estos enlaces",
    restText: (count) =>
      `Un parche reemplaza ${count === 1 ? "1 enlace muerto" : `${count} enlaces muertos`} por su nuevo hogar o su última copia sana. Revisalo antes de aplicarlo.`,
    restDownload: "Descargar parche",
    restApply: "Aplicalo desde tu repositorio con",
    preserveTitle: "Preservá a los vivos",
    preserveText: (count) =>
      `Pedile al Internet Archive que guarde hasta ${count} ${count === 1 ? "enlace vivo" : "enlaces vivos"} sin copia de este mes, antes de que también se vuelvan fantasmas.`,
    preserveAction: "Preservar enlaces vivos",
    preserveProgress: (sent, total) =>
      `Enviando páginas al Internet Archive, ${sent} de ${total}`,
    preserveDone: (safe) =>
      `${safe === 1 ? "1 página está a salvo" : `${safe} páginas están a salvo`} en el Internet Archive o guardándose ahora.`,
    preserveQueued: "Guardando",
    preserveFailed: "No guardada",
    preserveRecent: "Ya guardada hace poco",
    preserveWaiting:
      "El Internet Archive está ocupado con estas páginas. Esperando un minuto antes de la siguiente.",
    houseTitle:
      "Las ventanas se encienden en proporción a tus enlaces y cada enlace muerto descansa en una tumba.",
    houseLegend: {
      alive: "Encendida, vivo",
      unknown: "Titila, sin confirmar",
      ghost: "Ventana oscura y una tumba, muerto",
    },
    houseHint: "Elegí un fantasma para leer su autopsia.",
    houseShowing: (shown, total) =>
      `El jardín muestra ${shown} de ${total} tumbas.`,
    tally: {
      ghost: "muertos",
      unknown: "sin confirmar",
      alive: "siguen vivos",
    },
    nextTitle: "Qué podés hacer ahora",
    rowCause: "Causa de muerte",
    rowMemory: "Memoria",
    rowAfterlife: "Más allá",
    unknownHint:
      "Estos enlaces respondieron de una forma que Linkmortem no puede probar como muerta ni viva. Abrilos vos antes de cambiar algo.",
    modelMissing: (count) => {
      const pages =
        count === 1
          ? "1 página sospechosa quedó"
          : `${count} páginas sospechosas quedaron`;
      return `Gemma no estuvo disponible en este escaneo, así que ${pages} sin confirmar. El resto de los controles se hizo igual. Probá de nuevo en unos minutos.`;
    },
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
      model_unavailable: "Gemma no estuvo disponible para leerla",
      missing_section: "La sección ya no existe",
    },
    scanErrors: {
      invalid_target:
        "Ingresá una dirección web pública que empiece con http o https.",
      repository_not_found: "Ese repositorio no existe o no es público.",
      source_unreachable:
        "La fuente no respondió. Probá de nuevo en unos minutos.",
      github_rate_limited:
        "Se agotó el límite por hora de GitHub para este servidor. Probá en una hora o configurá GITHUB_TOKEN en el backend.",
      scan_not_found: "Esa autopsia no existe o ya venció.",
      preserve_unavailable:
        "Preservar páginas no está configurado en este servidor.",
      already_preserved:
        "Los enlaces vivos de esta autopsia ya se enviaron al archivo.",
      nothing_found: "No se encontraron enlaces en esa dirección.",
      too_many_scans:
        "Llegaste al límite de escaneos. Probá de nuevo en unos minutos.",
      busy: "Linkmortem está ocupado con otros escaneos. Probá de nuevo en un minuto.",
      unavailable:
        "El escaneo se cortó inesperadamente. Revisá tu conexión y probá de nuevo.",
    },
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
        text: "Reúne hasta 150 enlaces de las páginas de un sitio o de los archivos Markdown de un repositorio público, y avisa cuando había más.",
      },
      {
        title: "Diagnosticar",
        text: "Revisa cada enlace, hasta la sección a la que apunta, y detecta páginas que responden pero están muertas por dentro, como dominios en venta o errores disfrazados.",
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
        text: "Escribe un parche con los reemplazos que puede probar y la evidencia de cada uno. La Action de GitHub lo convierte en un pull request.",
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
    footer: {
      memoriam: "En memoria",
      epitaph:
        "Aquí yacen los enlaces que no llevaban a ningún lado. Que descansen, y que sus páginas sean recordadas.",
      note: "Linkmortem solo lee páginas públicas y nunca edita nada por su cuenta.",
      navigation: "Pie de página",
      groups: {
        autopsy: "La autopsia",
        project: "El proyecto",
        credits: "Lo mantienen vivo",
      },
      links: {
        scan: "Buscar enlaces muertos",
        action: "Action de GitHub",
        actionDemo: "Demo de la Action",
        source: "Código fuente",
        contributing: "Cómo contribuir",
        security: "Reportar una vulnerabilidad",
        license: "Licencia MIT",
        wayback: "Wayback Machine del Internet Archive",
        gemma: "Gemma, un modelo abierto de Google",
      },
      rights: "Código bajo licencia MIT. Hecho para el",
      challenge: "Hacktoberfest Open Source AI Challenge de DEV",
      disclaimer:
        "Los resultados son automáticos y pueden fallar, así que revisá cada reemplazo antes de usarlo. Las copias archivadas pertenecen al Internet Archive y a sus autores originales. Linkmortem no está afiliado al Internet Archive ni a Google.",
    },
  },
};
