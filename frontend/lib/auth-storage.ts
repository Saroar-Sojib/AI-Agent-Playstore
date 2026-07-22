// Access tokens are kept in localStorage, namespaced per agent slug — a
// browser can hold a signed-in session for multiple agents at once, each
// independent (mirrors the backend's per-agent login isolation). The
// refresh-token cookie is httpOnly and backend-managed; this only ever
// touches the short-lived access token.

const keyFor = (slug: string) => `agenthub:token:${slug}`;

export function getToken(slug: string): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(keyFor(slug));
}

export function setToken(slug: string, token: string): void {
  window.localStorage.setItem(keyFor(slug), token);
}

export function clearToken(slug: string): void {
  window.localStorage.removeItem(keyFor(slug));
}
