"use client";

import { useMemo, useState } from "react";
import type { Agent } from "@/lib/api";
import AgentCard from "./AgentCard";

export default function CatalogBrowser({ agents }: { agents: Agent[] }) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return agents;
    return agents.filter(
      (a) =>
        a.profession?.toLowerCase().includes(q) ||
        a.industry?.toLowerCase().includes(q) ||
        a.slug.toLowerCase().includes(q)
    );
  }, [agents, query]);

  return (
    <div className="flex flex-col gap-6">
      <div className="relative">
        <svg
          className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by profession or industry…"
          className="w-full rounded-xl border border-[var(--border-subtle)] bg-[var(--surface)] py-3 pl-10 pr-4 text-sm shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30"
          aria-label="Search agents"
        />
      </div>

      <p className="text-sm font-medium text-neutral-500 dark:text-neutral-400">
        {filtered.length} of {agents.length} agents
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-neutral-500 dark:text-neutral-400">
          No agents match “{query}”.
        </p>
      )}
    </div>
  );
}
