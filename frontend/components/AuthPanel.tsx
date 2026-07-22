"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth-storage";

type Mode = "login" | "signup";

export default function AuthPanel({ agentSlug }: { agentSlug: string }) {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const bundle =
        mode === "login"
          ? await api.login(agentSlug, email, password)
          : await api.signup(agentSlug, email, password);
      setToken(agentSlug, bundle.access_token);
      router.push(`/agents/${agentSlug}/chat`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6 rounded-2xl border border-[var(--border-subtle)] bg-[var(--surface)] p-6 shadow-lg shadow-indigo-500/5">
      <div className="flex rounded-xl bg-neutral-100 p-1 dark:bg-white/10">
        {(["login", "signup"] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => {
              setMode(m);
              setError(null);
            }}
            className={`flex-1 rounded-lg py-2 text-sm font-semibold transition ${
              mode === m
                ? "bg-[var(--surface)] text-indigo-700 shadow dark:text-indigo-300"
                : "text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200"
            }`}
            aria-pressed={mode === m}
          >
            {m === "login" ? "Log in" : "Sign up"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium text-neutral-700 dark:text-neutral-300">
            Email
          </span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-xl border border-[var(--border-subtle)] bg-transparent px-3.5 py-2.5 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30"
            autoComplete="email"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-sm">
          <span className="font-medium text-neutral-700 dark:text-neutral-300">
            Password
          </span>
          <input
            type="password"
            required
            minLength={mode === "signup" ? 6 : undefined}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-xl border border-[var(--border-subtle)] bg-transparent px-3.5 py-2.5 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>

        {error && (
          <p className="rounded-xl bg-red-50 px-3.5 py-2.5 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="brand-gradient-bg rounded-xl px-4 py-3 text-sm font-semibold text-white shadow-md shadow-indigo-500/25 transition hover:brightness-110 disabled:opacity-60"
        >
          {loading
            ? "Please wait…"
            : mode === "login"
              ? "Log in"
              : "Create account"}
        </button>
      </form>

      <p className="text-center text-xs text-neutral-500 dark:text-neutral-400">
        This login only works for this agent — a separate account is needed
        for each agent you use.
      </p>
    </div>
  );
}
