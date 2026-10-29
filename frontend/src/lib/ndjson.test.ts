import { describe, expect, it } from "vitest";
import { readLines } from "./ndjson";

function streamOf(...chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      chunks.forEach((chunk) => controller.enqueue(encoder.encode(chunk)));
      controller.close();
    },
  });
}

describe("readLines", () => {
  it("joins lines split across chunks", async () => {
    const lines: string[] = [];
    for await (const line of readLines(streamOf('{"a":', '1}\n{"b"', ":2}\n")))
      lines.push(line);
    expect(lines).toEqual(['{"a":1}', '{"b":2}']);
  });
});
