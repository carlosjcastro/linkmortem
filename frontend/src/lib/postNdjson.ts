import { readLines } from "./ndjson";

export type StreamRefusal = { type: "error"; code: string; message: string };

export async function* postNdjson<Event>(
  url: string,
  body: unknown,
  signal: AbortSignal,
): AsyncGenerator<Event | StreamRefusal> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
    signal,
  });
  if (!response.ok || !response.body) {
    const refusal = await response.json().catch(() => ({}));
    yield {
      type: "error",
      code: refusal.code ?? "unavailable",
      message: refusal.message ?? "",
    };
    return;
  }
  for await (const line of readLines(response.body)) {
    yield JSON.parse(line) as Event;
  }
}
