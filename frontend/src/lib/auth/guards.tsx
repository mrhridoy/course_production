"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/features/auth/store";
import type { UserRole } from "@/lib/api/types";

interface RoleGuardProps {
  allow: UserRole[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({ allow, children, fallback = null }: RoleGuardProps) {
  const { user, isHydrated, hydrate } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isHydrated) hydrate();
  }, [isHydrated, hydrate]);

  useEffect(() => {
    if (isHydrated && !user) router.replace("/login");
  }, [isHydrated, user, router]);

  if (!isHydrated) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-neutral-500">
        Loading…
      </div>
    );
  }
  if (!user) return null;
  if (!allow.includes(user.role)) {
    return (
      <>
        {fallback ?? (
          <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
            You don&apos;t have permission to view this page.
          </div>
        )}
      </>
    );
  }
  return <>{children}</>;
}
