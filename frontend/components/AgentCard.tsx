import Link from "next/link";
import type { Agent } from "@/lib/api";
import { colorFor } from "@/lib/badge-colors";

export default function AgentCard({ agent }: { agent: Agent }) {
  const label = agent.industry ?? "General";
  const color = colorFor(label);
  const initial = (agent.profession ?? agent.slug).charAt(0).toUpperCase();

  return (
    <Link
      href={`/agents/${agent.slug}`}
      className="group flex flex-col gap-3 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-4 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-indigo-500/10"
    >
      <div className="flex items-start justify-between gap-2">
        <span
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${color.bg} ${color.fg}`}
        >
          {initial}
        </span>
        <span
          className={`rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide ${color.bg} ${color.fg}`}
        >
          {label}
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-base font-semibold text-neutral-900 transition group-hover:text-indigo-600 dark:text-neutral-100 dark:group-hover:text-indigo-300">
          {agent.profession ?? agent.slug}
        </span>
        <span className="inline-flex items-center gap-1 text-sm text-neutral-500 transition group-hover:gap-1.5 group-hover:text-indigo-500 dark:text-neutral-400">
          Chat with this agent
          <span aria-hidden="true">→</span>
        </span>
      </div>
    </Link>
  );
}
