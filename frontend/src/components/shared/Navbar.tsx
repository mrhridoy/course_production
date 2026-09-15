"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useAuthStore } from "@/features/auth/store";
import { Button } from "@/components/ui/button";
import { useLogout } from "@/features/auth/hooks";

export function Navbar() {
  const { user, isHydrated, hydrate } = useAuthStore();
  const logout = useLogout();

  useEffect(() => {
    if (!isHydrated) hydrate();
  }, [isHydrated, hydrate]);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-neutral-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link href="/" className="text-base font-semibold tracking-tight">
          ICT<span className="text-brand-600">Bangladesh</span>
        </Link>
        <nav className="flex items-center gap-1">
          <Link
            href="/courses"
            className="rounded-md px-3 py-2 text-sm hover:bg-neutral-100"
          >
            Courses
          </Link>
          {user ? (
            <>
              <Link href="/dashboard">
                <Button variant="outline" size="sm">
                  Dashboard
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={logout}>
                Logout
              </Button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Sign up</Button>
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
