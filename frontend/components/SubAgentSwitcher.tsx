"use client";

import type { SubAgent } from "@/lib/api";

export default function SubAgentSwitcher({
  subAgents,
  selected,
  onSelect,
}: {
  subAgents: SubAgent[];
  selected: SubAgent | null;
  onSelect: (subAgent: SubAgent | null) => void;
}) {
  if (subAgents.length === 0) return null;

  const items: Array<{ key: string; label: string; sub: SubAgent | null }> = [
    { key: "main", label: "Main agent", sub: null },
    ...subAgents
      .slice()
      .sort((a, b) => a.order_index - b.order_index)
      .map((s) => ({ key: String(s.id), label: s.name, sub: s })),
  ];

  return (
    <div className="flex flex-col gap-2 md:w-56">
      <span className="hidden px-1 text-xs font-semibold uppercase tracking-wide text-neutral-400 md:block">
        Chat with
      </span>
      <nav
        aria-label="Sub-agent switcher"
        className="flex gap-2 overflow-x-auto pb-1 md:flex-col md:overflow-visible md:pb-0"
      >
        {items.map((item) => {
          const isActive = selected?.id === item.sub?.id;
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => onSelect(item.sub)}
              className={`flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-2.5 text-left text-sm font-medium transition md:w-full ${
                isActive
                  ? "brand-gradient-bg text-white shadow-md shadow-indigo-500/25"
                  : "bg-neutral-100 text-neutral-700 hover:bg-neutral-200 dark:bg-white/10 dark:text-neutral-300 dark:hover:bg-white/20"
              }`}
              aria-pressed={isActive}
            >
              <span
                className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                  isActive ? "bg-white" : "bg-neutral-400 dark:bg-neutral-500"
                }`}
                aria-hidden="true"
              />
              {item.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
