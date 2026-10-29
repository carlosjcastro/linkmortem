const BLOB = /^https:\/\/github\.com\/[^/]+\/[^/]+\/blob\/[^/]+\/(.+)$/;

export function sourceLabel(source: string): string {
  const match = BLOB.exec(source);
  return match ? decodeURIComponent(match[1]) : source;
}
