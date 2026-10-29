export const MAX_TARGET_LENGTH = 300;

const ALLOWED_PROTOCOLS = new Set(["http:", "https:"]);
const HIDDEN_CHARACTERS = /[\s\u0000-\u001f\u007f]/;

export type TargetProblem = "invalid" | "credentials" | "port" | "length";

export type TargetCheck =
  { ok: true; target: string } | { ok: false; problem: TargetProblem };

const refuse = (problem: TargetProblem): TargetCheck => ({
  ok: false,
  problem,
});

export function checkTarget(input: string): TargetCheck {
  const trimmed = input.trim();
  if (!trimmed || HIDDEN_CHARACTERS.test(trimmed)) return refuse("invalid");
  if (trimmed.length > MAX_TARGET_LENGTH) return refuse("length");
  const candidate = /^[a-z][a-z0-9+.-]*:/i.test(trimmed)
    ? trimmed
    : `https://${trimmed}`;
  let url: URL;
  try {
    url = new URL(candidate);
  } catch {
    return refuse("invalid");
  }
  if (!ALLOWED_PROTOCOLS.has(url.protocol) || !url.hostname.includes("."))
    return refuse("invalid");
  if (url.username || url.password) return refuse("credentials");
  if (url.port) return refuse("port");
  return { ok: true, target: url.toString() };
}
