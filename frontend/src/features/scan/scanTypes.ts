export type Verdict = "alive" | "ghost" | "unknown";

export type Cause =
  | "alive"
  | "unreadable"
  | "not_found"
  | "gone"
  | "dns_failure"
  | "parked_domain"
  | "error_page"
  | "placeholder"
  | "unrelated_redirect"
  | "server_error"
  | "unreachable"
  | "timeout"
  | "restricted"
  | "blocked"
  | "unclassified"
  | "model_unavailable";

export type Diagnosis = {
  link: { url: string; source: string; text: string };
  verdict: Verdict;
  cause: Cause;
  status_code: number | null;
  final_url: string | null;
  evidence: string;
};

export type Memory = {
  status: "found" | "missing" | "unavailable";
  archived_url: string;
  captured_on: string;
  title: string;
  excerpt: string;
};

export type Afterlife = {
  status: "found" | "none" | "unavailable" | "skipped";
  url: string;
  title: string;
  match: "same" | "successor" | "different" | null;
  evidence: string;
  source: "search" | "graveyard" | "";
};

export type ScanEvent =
  | { type: "collected"; total: number; reincarnation: boolean }
  | { type: "link"; diagnosis: Diagnosis }
  | { type: "memory"; url: string; memory: Memory }
  | { type: "afterlife"; url: string; afterlife: Afterlife }
  | { type: "saved"; id: string }
  | { type: "done"; summary: Partial<Record<Verdict, number>> }
  | { type: "error"; code: string; message: string };
