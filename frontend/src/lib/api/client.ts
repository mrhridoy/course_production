import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from "axios";
import { endpoints } from "./endpoints";
import { tokenStorage } from "../auth/storage";
import type { AuthTokens } from "./types";

// ── Browser client ────────────────────────────────────────────────────────────
// Always uses a RELATIVE base path so the request goes to the same origin
// (the Next.js server), which then proxies it to the FastAPI container via the
// rewrites defined in next.config.ts.  This works in every environment:
//   • Production Docker : browser → /api/v1/… → Next.js rewrite → deployment:8000
//   • Local dev         : browser → /api/v1/… → Next.js dev rewrite → localhost:8000
// Never set this to an absolute URL or you risk leaking internal hostnames to
// the browser and triggering Mixed-Content errors on HTTPS pages.
const apiBasePath = process.env.NEXT_PUBLIC_API_BASE_PATH ?? "/api/v1";

export const api = axios.create({
  baseURL: apiBasePath,
  timeout: 20_000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.set("Authorization", `Bearer ${token}`);
  }
  return config;
});

type RetriableConfig = AxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  if (refreshPromise) return refreshPromise;
  const refresh = tokenStorage.getRefresh();
  if (!refresh) throw new Error("No refresh token");

  refreshPromise = axios
    .post<AuthTokens>(`${apiBasePath}${endpoints.auth.refresh}`, { refresh_token: refresh })
    .then((res) => {
      tokenStorage.setAccess(res.data.access_token);
      return res.data.access_token;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const status = error.response?.status;

    if (
      status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes(endpoints.auth.refresh) &&
      !original.url?.includes(endpoints.auth.login)
    ) {
      original._retry = true;
      try {
        const newToken = await refreshAccessToken();
        original.headers = {
          ...(original.headers ?? {}),
          Authorization: `Bearer ${newToken}`,
        };
        return api.request(original);
      } catch (refreshErr) {
        tokenStorage.clear();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshErr);
      }
    }

    return Promise.reject(error);
  }
);

export function extractApiError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
    return err.message;
  }
  if (err instanceof Error) return err.message;
  return "Something went wrong";
}

// ── Server-only client ────────────────────────────────────────────────────────
// Used for any axios calls that run in a Node.js context (Route Handlers,
// Server Actions, etc.).  Needs an absolute URL because Node.js has no implicit
// base origin.  Prefers API_URL (internal Docker) → NEXT_PUBLIC_API_URL → localhost.
const serverBaseURL = `${
  process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
}${apiBasePath}`;

export const serverApi = axios.create({
  baseURL: serverBaseURL,
  timeout: 20_000,
  headers: { "Content-Type": "application/json" },
});
