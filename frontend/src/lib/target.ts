const ALLOWED_PROTOCOLS = new Set(["http:", "https:"]);

export function normalizeTarget(input: string): string | null {
  const trimmed = input.trim();
  if (!trimmed) return null;
  const candidate = /^[a-z]+:\/\//i.test(trimmed)
    ? trimmed
    : `https://${trimmed}`;
  try {
    const url = new URL(candidate);
    if (!ALLOWED_PROTOCOLS.has(url.protocol) || !url.hostname.includes("."))
      return null;
    return url.toString();
  } catch {
    return null;
  }
}
