/**
 * Normalise a media URL so it's always safe to render in the browser.
 *
 * The FastAPI schema validator may return absolute URLs using whatever
 * BASE_URL was set on the server (e.g. "http://localhost:8000/uploads/…" or
 * "http://deployment:8000/uploads/…").  Those internal hostnames must never
 * reach the browser — they trigger Mixed-Content blocks on HTTPS pages and
 * DNS-resolution failures.
 *
 * Strategy
 * ─────────
 * Server-side (SSR / RSC):
 *   Use the internal Docker URL (API_URL env var) so image fetches work inside
 *   the Docker network during server rendering.
 *
 * Client-side (browser):
 *   Strip any origin prefix and return a root-relative path like
 *   "/uploads/thumbnails/abc.jpg".  The Next.js rewrite rule
 *   `/uploads/:path*` → `http://deployment:8000/uploads/:path*`
 *   proxies the request transparently, so the browser only ever sees
 *   same-origin URLs — no Mixed-Content, no internal hostnames.
 */
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;

  // ── Server-side ────────────────────────────────────────────────────────────
  if (typeof window === "undefined") {
    // Already a proper internal absolute URL — use as-is.
    if (url.startsWith("http://") || url.startsWith("https://")) return url;
    // Relative path — prepend the internal API base URL.
    const base = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return `${base}${url.startsWith("/") ? "" : "/"}${url}`;
  }

  // ── Client-side ────────────────────────────────────────────────────────────
  // Strip any origin prefix so we always get a root-relative path.
  // This handles:  http://localhost:8000/uploads/…
  //                http://deployment:8000/uploads/…
  //                https://student.ictbangladesh.bd/uploads/…
  //                /uploads/…   (already relative)
  if (url.startsWith("http://") || url.startsWith("https://")) {
    try {
      const parsed = new URL(url);
      // Return just the path+search — e.g. "/uploads/thumbnails/abc.jpg"
      return parsed.pathname + parsed.search;
    } catch {
      // Malformed URL — fall through to the relative-path return below
    }
  }
  return url.startsWith("/") ? url : `/${url}`;
}

export function formatBDT(amount: number): string {
  return new Intl.NumberFormat("en-BD", {
    style: "currency",
    currency: "BDT",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Intl.DateTimeFormat("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(new Date(iso));
  } catch {
    return "—";
  }
}
