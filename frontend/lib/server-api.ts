// For Server Components only. A Server Component's fetch() runs as plain
// Node.js code, not through Next's own HTTP layer — next.config.ts's
// rewrites() only rewrites requests that actually arrive over HTTP (i.e.
// from the browser), so a relative "/api/..." URL doesn't resolve here.
// This talks to the backend directly via its absolute URL instead.

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function serverFetch<T>(path: string): Promise<T | null> {
  const res = await fetch(`${BACKEND_URL}/api${path}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) {
    throw new Error(`Backend request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}
