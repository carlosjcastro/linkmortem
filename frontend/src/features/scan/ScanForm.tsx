import { useId, useState, type FormEvent } from "react";
import { normalizeTarget } from "../../lib/target";
import { useTranslation } from "../i18n/useTranslation";

type ScanFormProps = { onScan: (target: string) => void; busy?: boolean };

export default function ScanForm({ onScan, busy = false }: ScanFormProps) {
  const { t } = useTranslation();
  const [value, setValue] = useState("");
  const [invalid, setInvalid] = useState(false);
  const inputId = useId();
  const hintId = useId();

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const target = normalizeTarget(value);
    setInvalid(target === null);
    if (target) onScan(target);
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
      <p id={hintId} role={invalid ? "alert" : undefined} className={`mt-3 text-[0.95rem] ${invalid ? "text-rose" : "text-dusk"}`}>
        {invalid ? t.targetInvalid : t.targetHint}
      </p>
    </form>
  );
}
