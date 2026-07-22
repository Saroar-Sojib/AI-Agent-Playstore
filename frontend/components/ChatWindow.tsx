"use client";

import { useEffect, useRef, useState } from "react";

export interface DisplayMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

function Avatar({ role }: { role: "user" | "assistant" }) {
  if (role === "assistant") {
    return (
      <div className="brand-gradient-bg flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white">
        AI
      </div>
    );
  }
  return (
    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-neutral-200 text-[11px] font-bold text-neutral-600 dark:bg-white/15 dark:text-neutral-300">
      You
    </div>
  );
}

export default function ChatWindow({
  messages,
  onSend,
  sending,
  error,
  placeholder,
}: {
  messages: DisplayMessage[];
  onSend: (text: string) => void;
  sending: boolean;
  error: string | null;
  placeholder: string;
}) {
  const [text, setText] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || sending) return;
    onSend(trimmed);
    setText("");
  }

  return (
    <div className="flex flex-1 flex-col rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] shadow-sm">
      <div className="min-h-[16rem] max-h-[60vh] flex-1 space-y-4 overflow-y-auto p-4 sm:p-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-2 py-12 text-center">
            <div className="brand-gradient-bg flex h-11 w-11 items-center justify-center rounded-2xl text-lg">
              💬
            </div>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              No messages yet — say hello.
            </p>
          </div>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-end gap-2 ${m.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <Avatar role={m.role} />
            <div
              className={`max-w-[75%] whitespace-pre-wrap px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
                m.role === "user"
                  ? "brand-gradient-bg rounded-2xl rounded-br-md text-white"
                  : "rounded-2xl rounded-bl-md bg-neutral-100 text-neutral-900 dark:bg-white/10 dark:text-neutral-100"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex flex-col gap-1.5">
            <div className="flex items-end gap-2">
              <Avatar role="assistant" />
              <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-neutral-100 px-4 py-3 dark:bg-white/10">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400 [animation-delay:-0.3s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400 [animation-delay:-0.15s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-neutral-400" />
              </div>
            </div>
            <p className="pl-9 text-xs text-neutral-400 dark:text-neutral-500">
              This app runs on a free-tier server, so the first reply can take up to a minute to wake up. Thanks for your patience!
            </p>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {error && (
        <p className="border-t border-[var(--border-subtle)] bg-red-50 px-4 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        className="flex gap-2 border-t border-[var(--border-subtle)] p-3"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={placeholder}
          disabled={sending}
          className="flex-1 rounded-xl border border-[var(--border-subtle)] bg-transparent px-3.5 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={sending || !text.trim()}
          className="brand-gradient-bg rounded-xl px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-indigo-500/25 transition hover:brightness-110 disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </div>
  );
}
