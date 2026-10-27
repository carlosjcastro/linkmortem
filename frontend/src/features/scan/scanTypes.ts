export type Verdict = "alive" | "ghost" | "unknown";

export type Cause =
  | "alive"
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
  | "unclassified";

export type Diagnosis = {
  link: { url: string; source: string; text: string };
  verdict: Verdict;
  cause: Cause;
  status_code: number | null;
  final_url: string | null;
  evidence: string;
};

export type ScanEvent =
  | { type: "collected"; total: number }
  | { type: "link"; diagnosis: Diagnosis }
  | { type: "done"; summary: Partial<Record<Verdict, number>> }
  | { type: "error"; code: string; message: string };
