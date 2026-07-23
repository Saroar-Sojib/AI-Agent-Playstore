"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, withAutoRefresh, type Agent, type SubAgent } from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth-storage";
import ChatWindow, { type DisplayMessage } from "@/components/ChatWindow";
import SubAgentSwitcher from "@/components/SubAgentSwitcher";
import SiteHeader from "@/components/SiteHeader";
import { colorFor } from "@/lib/badge-colors";

export default function ChatPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const router = useRouter();

  const [token, setTokenState] = useState<string | null>(null);
  const [agent, setAgent] = useState<Agent | null>(null);
  const [subAgents, setSubAgents] = useState<SubAgent[]>([]);
  const [selected, setSelected] = useState<SubAgent | null>(null);
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | undefined>();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Each target (main agent or a specific sub-agent) has its own
  // conversation — keep them separate so switching back and forth within
  // the same session doesn't lose what was already said to the other one.
  const [threads, setThreads] = useState<
    Record<string, { conversationId?: number; messages: DisplayMessage[] }>
  >({});

  // Auth guard — this page requires a token scoped to THIS agent specifically.
  useEffect(() => {
    const existing = getToken(slug);
    if (!existing) {
      router.replace(`/agents/${slug}`);
      return;
    }
    // getToken reads localStorage (client-only); setting it during render
    // would mismatch the server-rendered HTML, so this must run post-mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setTokenState(existing);
  }, [slug, router]);

  // Load the agent + its sub-agents (public endpoints) once we know we're
  // staying on this page.
  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const [agentData, subAgentData] = await Promise.all([
          api.getAgent(slug),
          api.listSubAgents(slug),
        ]);
        if (cancelled) return;
        setAgent(agentData);
        setSubAgents(subAgentData);
      } catch {
        if (!cancelled) setError("Could not load this agent. Try refreshing.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [slug, token]);

  function targetKey(subAgent: SubAgent | null): string {
    return subAgent ? `sub-${subAgent.id}` : "main";
  }

  function switchTarget(subAgent: SubAgent | null) {
    const currentKey = targetKey(selected);
    const nextKey = targetKey(subAgent);
    const saved = threads[nextKey];

    setThreads((prev) => ({ ...prev, [currentKey]: { conversationId, messages } }));
    setSelected(subAgent);
    setMessages(saved?.messages ?? []);
    setConversationId(saved?.conversationId);
    setError(null);
  }

  function handleLogout() {
    if (token) api.logout(token).catch(() => {});
    clearToken(slug);
    router.push(`/agents/${slug}`);
  }

  async function handleSend(text: string) {
    if (!token) return;
    setError(null);
    setSending(true);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text, id: `local-${prev.length}` },
    ]);

    try {
      const call = (tok: string) =>
        selected
          ? api.chatWithSubAgent(slug, selected.id, text, tok, conversationId)
          : api.chatWithAgent(slug, text, tok, conversationId);

      const result = await withAutoRefresh(token, call, (newToken) => {
        setToken(slug, newToken);
        setTokenState(newToken);
      });

      setConversationId(result.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.reply, id: `local-${prev.length}` },
      ]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setError("This account isn't scoped to this agent.");
      } else if (err instanceof ApiError && err.status === 429) {
        setError("You're sending messages too fast — please slow down.");
      } else if (err instanceof ApiError && err.status === 502) {
        setError("The AI service is unavailable right now. Try again shortly.");
      } else {
        setError("Something went wrong sending that message.");
      }
    } finally {
      setSending(false);
    }
  }

  if (!token) return null; // redirecting

  const label = agent?.industry ?? "…";
  const color = colorFor(label);
  const initial = (agent?.profession ?? slug).charAt(0).toUpperCase();

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <SiteHeader
        right={
          <button
            onClick={handleLogout}
            className="rounded-xl border border-[var(--border-subtle)] px-3.5 py-1.5 text-sm font-medium text-neutral-600 transition hover:bg-black/5 dark:text-neutral-300 dark:hover:bg-white/10"
          >
            Log out
          </button>
        }
      />

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-4 px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3 border-b border-[var(--border-subtle)] pb-4">
          <span
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${color.bg} ${color.fg}`}
          >
            {initial}
          </span>
          <div>
            <span className="text-xs font-medium uppercase tracking-wide text-neutral-400">
              {label}
            </span>
            <h1 className="text-lg font-bold leading-tight text-neutral-900 dark:text-neutral-50">
              {agent?.profession ?? slug}
            </h1>
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-4 md:flex-row">
          <SubAgentSwitcher
            subAgents={subAgents}
            selected={selected}
            onSelect={switchTarget}
          />

          <div className="flex flex-1 flex-col">
            <ChatWindow
              messages={messages}
              onSend={handleSend}
              sending={sending}
              error={error}
              placeholder={
                selected
                  ? `Ask the ${selected.name} something…`
                  : `Ask this agent something…`
              }
            />
          </div>
        </div>
      </main>
    </div>
  );
}
