import { useId, useState, type FormEvent } from "react";
import { EXAMPLE_TARGET } from "../../lib/example";
import {
  checkTarget,
  MAX_TARGET_LENGTH,
  type TargetProblem,
} from "../../lib/target";
import { useTranslation } from "../i18n/useTranslation";

type ScanFormProps = { onScan: (target: string) => void; busy?: boolean };

export default function ScanForm({ onScan, busy = false }: ScanFormProps) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const [problem, setProblem] = useState<TargetProblem | null>(null);
  const invalid = problem !== null;
  const inputId = useId();
  const hintId = useId();

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const check = checkTarget(value);
    setProblem(check.ok ? null : check.problem);
    if (check.ok) onScan(check.target);
  };

  const tryExample = () => {
    setValue(EXAMPLE_TARGET);
    setProblem(null);
    onScan(EXAMPLE_TARGET);
  };

  return (
    <form onSubmit={submit} noValidate className="mt-12 w-full max-w-xl">
      <label htmlFor={inputId} className="block text-dusk">
        {t.targetLabel}
      </label>
      <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end">
        <input
          id={inputId}
          type="url"
          inputMode="url"
          autoComplete="url"
          spellCheck={false}
          maxLength={MAX_TARGET_LENGTH}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={t.targetPlaceholder}
          aria-describedby={hintId}
          aria-invalid={invalid}
          className="min-w-0 flex-1 border-b-2 border-veil bg-transparent pb-3 pt-2 text-lg text-bone outline-none transition-colors placeholder:text-dusk/70 focus:border-spectral aria-invalid:border-rose"
        />
        <button
          type="submit"
          disabled={busy}
          className="rounded-full bg-marigold px-7 py-3.5 font-semibold text-night-deep transition-[transform,background-color] hover:bg-bone active:scale-[0.97] disabled:cursor-progress disabled:opacity-70"
        >
          {t.scanAction}
        </button>
      </div>
      <p
        id={hintId}
        role={invalid ? "alert" : undefined}
        className={`mt-3 text-[0.95rem] ${invalid ? "text-rose" : "text-dusk"}`}
      >
        {problem ? t.targetProblems[problem] : t.targetHint}
      </p>
      <button
        type="button"
        onClick={tryExample}
        disabled={busy}
        className="mt-4 rounded-md text-[0.95rem] text-spectral underline decoration-spectral/40 underline-offset-4 hover:decoration-spectral focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-marigold disabled:cursor-progress disabled:opacity-70"
      >
        {t.tryExample}
      </button>
    </form>
  );
}
