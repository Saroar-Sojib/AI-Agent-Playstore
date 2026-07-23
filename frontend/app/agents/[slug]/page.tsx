import { notFound } from "next/navigation";
import type { Agent } from "@/lib/api";
import { serverFetch } from "@/lib/server-api";
import AuthPanel from "@/components/AuthPanel";
import SiteHeader from "@/components/SiteHeader";

export default async function AgentPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const agent = await serverFetch<Agent>(`/v1/agents/${slug}`);
  if (!agent) notFound();

  const label = agent.industry ?? "General";
  const initial = (agent.profession ?? agent.slug).charAt(0).toUpperCase();

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <SiteHeader />

      <main className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center gap-8 px-4 py-10 sm:px-6">
        <header className="flex flex-col items-center gap-3 text-center">
          <span className="brand-gradient-bg flex h-14 w-14 items-center justify-center rounded-2xl text-xl font-bold text-white">
            {initial}
          </span>
          <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-neutral-600 dark:bg-white/10 dark:text-neutral-300">
            {label}
          </span>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
            {agent.profession ?? agent.slug}
          </h1>
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            Sign up or log in — this account only works for this agent.
          </p>
        </header>

        <AuthPanel agentSlug={agent.slug} />
      </main>
    </div>
  );
}
