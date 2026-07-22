// Deterministic accent color per industry name, so the catalog reads as
// lively/varied without any per-agent config — purely derived from the
// string itself.
const PALETTE = [
  { bg: "bg-violet-100 dark:bg-violet-500/15", fg: "text-violet-700 dark:text-violet-300" },
  { bg: "bg-indigo-100 dark:bg-indigo-500/15", fg: "text-indigo-700 dark:text-indigo-300" },
  { bg: "bg-sky-100 dark:bg-sky-500/15", fg: "text-sky-700 dark:text-sky-300" },
  { bg: "bg-teal-100 dark:bg-teal-500/15", fg: "text-teal-700 dark:text-teal-300" },
  { bg: "bg-amber-100 dark:bg-amber-500/15", fg: "text-amber-700 dark:text-amber-300" },
  { bg: "bg-rose-100 dark:bg-rose-500/15", fg: "text-rose-700 dark:text-rose-300" },
  { bg: "bg-fuchsia-100 dark:bg-fuchsia-500/15", fg: "text-fuchsia-700 dark:text-fuchsia-300" },
  { bg: "bg-emerald-100 dark:bg-emerald-500/15", fg: "text-emerald-700 dark:text-emerald-300" },
];

export function colorFor(seed: string) {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return PALETTE[hash % PALETTE.length];
}
