const ACCESS_KEY = "ictbd.access_token";
const REFRESH_KEY = "ictbd.refresh_token";
const USER_KEY = "ictbd.user";
const COOKIE_NAME = "ictbd_auth";

export const tokenStorage = {
  getAccess(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(ACCESS_KEY);
  },
  getRefresh(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(REFRESH_KEY);
  },
  getUser<T = unknown>(): T | null {
    if (typeof window === "undefined") return null;
    const raw = window.localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  },
  set(access: string, refresh: string, user: unknown) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ACCESS_KEY, access);
    window.localStorage.setItem(REFRESH_KEY, refresh);
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
    setMarkerCookie();
  },
  setAccess(access: string) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ACCESS_KEY, access);
    setMarkerCookie();
  },
  clear() {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
    window.localStorage.removeItem(USER_KEY);
    clearMarkerCookie();
  },
};

function setMarkerCookie() {
  const isHttps = window.location.protocol === "https:";
  document.cookie = `${COOKIE_NAME}=1; Path=/; SameSite=Lax; Max-Age=2592000${isHttps ? "; Secure" : ""}`;
}

function clearMarkerCookie() {
  document.cookie = `${COOKIE_NAME}=; Path=/; Max-Age=0`;
}

export const AUTH_COOKIE_NAME = COOKIE_NAME;
