import type { ScanEvent } from "./scanTypes";

export type SavedScan = { target: string; events: ScanEvent[] };

const SHARE_PATH = /^\/r\/([A-Za-z0-9_-]{8,32})$/;

export function sharedScanId(pathname: string): string {
  return SHARE_PATH.exec(pathname)?.[1] ?? "";
}

export function shareUrl(id: string): string {
  return `${window.location.origin}/r/${id}`;
}

export async function fetchSavedScan(
  id: string,
  signal: AbortSignal,
): Promise<SavedScan | null> {
  const response = await fetch(`/api/scans/${id}`, { signal });
  return response.ok ? ((await response.json()) as SavedScan) : null;
}
