// Typed client for the AgentHub FastAPI backend. Every call goes through
// the same origin (`/api/...`) — next.config.ts rewrites that to the real
// backend, so no CORS handling or absolute backend URL is needed here.

export interface Agent {
  id: number;
  slug: string;
  industry: string | null;
  profession: string | null;
  created_at: string;
}

export interface AgentListResponse {
  data: Agent[];
  pagination: { page: number; page_size: number; total: number };
}

export interface SubAgent {
  id: number;
  name: string;
  task_description: string | null;
  order_index: number;
}

export interface TokenBundle {
  access_token: string;
  token_type: string;
  expires_in: number | null;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
}

export interface ChatResponse {
  conversation_id: number;
  reply: string;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...options,
    credentials: "include", // send/receive the httpOnly refresh-token cookie
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listAgents: (page = 1, pageSize = 100) =>
    request<AgentListResponse>(`/v1/agents/?page=${page}&page_size=${pageSize}`),

  getAgent: (slug: string) => request<Agent>(`/v1/agents/${slug}`),

  listSubAgents: (slug: string) =>
    request<SubAgent[]>(`/v1/agents/${slug}/sub-agents`),

  signup: (agentSlug: string, email: string, password: string) =>
    request<TokenBundle>(`/v1/auth/signup`, {
      method: "POST",
      body: JSON.stringify({ agent_slug: agentSlug, email, password }),
    }),

  login: (agentSlug: string, email: string, password: string) =>
    request<TokenBundle>(`/v1/auth/login`, {
      method: "POST",
      body: JSON.stringify({ agent_slug: agentSlug, email, password }),
    }),

  refresh: () => request<TokenBundle>(`/v1/auth/refresh`, { method: "POST" }),

  logout: (token: string) =>
    request<void>(`/v1/auth/logout`, { method: "POST" }, token),

  chatWithAgent: (
    slug: string,
    message: string,
    token: string,
    conversationId?: number
  ) =>
    request<ChatResponse>(
      `/v1/agents/${slug}/chat`,
      {
        method: "POST",
        body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
      },
      token
    ),

  chatWithSubAgent: (
    slug: string,
    subAgentId: number,
    message: string,
    token: string,
    conversationId?: number
  ) =>
    request<ChatResponse>(
      `/v1/agents/${slug}/sub-agents/${subAgentId}/chat`,
      {
        method: "POST",
        body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
      },
      token
    ),

  getMessages: (slug: string, conversationId: number, token: string) =>
    request<ChatMessage[]>(
      `/v1/agents/${slug}/conversations/${conversationId}/messages`,
      {},
      token
    ),
};

/** Calls `fn(token)`; on a 401, refreshes the access token once and retries. */
export async function withAutoRefresh<T>(
  token: string,
  fn: (token: string) => Promise<T>,
  onNewToken: (token: string) => void
): Promise<T> {
  try {
    return await fn(token);
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      const bundle = await api.refresh();
      onNewToken(bundle.access_token);
      return fn(bundle.access_token);
    }
    throw err;
  }
}
