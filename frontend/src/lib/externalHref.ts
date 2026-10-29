const WEB_PROTOCOLS = new Set(["http:", "https:"]);

export function externalHref(address: string): string | undefined {
  try {
    return WEB_PROTOCOLS.has(new URL(address).protocol) ? address : undefined;
  } catch {
    return undefined;
  }
}
