import { NextRequest, NextResponse } from "next/server";

const AUTH_COOKIE = "ictbd_auth";

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const hasAuth = req.cookies.get(AUTH_COOKIE)?.value === "1";

  if (pathname.startsWith("/dashboard") && !hasAuth) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("from", pathname);
    return NextResponse.redirect(url);
  }

  if ((pathname === "/login" || pathname === "/register") && hasAuth) {
    const url = req.nextUrl.clone();
    url.pathname = "/dashboard";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
};
