import type { ScanState } from "../scan/scanState";
import PreservePanel from "./PreservePanel";
import RestPanel from "./RestPanel";
import { isRepositoryScan, livingCount, replacementCount } from "./replacementCount";

export default function Aftercare({ state }: { state: ScanState }) {
  const replacements = isRepositoryScan(state.target) ? replacementCount(state) : 0;
  const living = livingCount(state);
  if (!state.shareId || (!replacements && !living)) return null;

  return (
    <div className="mt-10 grid gap-10 md:grid-cols-2">
      {replacements ? <RestPanel id={state.shareId} count={replacements} /> : null}
      {living ? <PreservePanel id={state.shareId} living={living} /> : null}
    </div>
  );
}
