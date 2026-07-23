import type { AgentListResponse } from "@/lib/api";
import { serverFetch } from "@/lib/server-api";
import CatalogBrowser from "@/components/CatalogBrowser";
import SiteHeader from "@/components/SiteHeader";
import BackendWakingUp from "@/components/BackendWakingUp";

export default async function HomePage() {
  let list: AgentListResponse | null;
  try {
    list = await serverFetch<AgentListResponse>(
      "/v1/agents/?page=1&page_size=100"
    );
  } catch {
    // Free-tier backend was asleep and didn't respond in time — show a
    // friendly wait screen instead of crashing the page.
    return (
      <div className="flex min-h-full flex-1 flex-col">
        <SiteHeader />
        <BackendWakingUp />
      </div>
    );
  }
  const agents = list?.data ?? [];

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <SiteHeader />

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-3">
          <span className="w-fit rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300">
            {agents.length} AI agents, one per profession
          </span>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50 sm:text-4xl">
            Pick an agent.{" "}
            <span className="brand-gradient-text">Chat in character.</span>
          </h1>
          <p className="max-w-2xl text-sm text-neutral-600 dark:text-neutral-400 sm:text-base">
            Every agent below is a real profession persona — sign up for that
            agent specifically, then chat with it (and its specialized
            sub-agents), powered by a real LLM.
          </p>
        </header>

        <CatalogBrowser agents={agents} />
      </main>

      <footer className="border-t border-[var(--border-subtle)] py-6 text-center text-xs text-neutral-400">
        AgentHub — a catalog of AI agent personas
      </footer>
    </div>
  );
}
