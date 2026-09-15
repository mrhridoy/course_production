"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/features/auth/store";

export default function DashboardIndex() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (!user) return;
    if (user.role === "student") router.replace("/dashboard/student");
    else if (user.role === "teacher") router.replace("/dashboard/teacher");
    else if (user.role === "admin") router.replace("/dashboard/admin");
  }, [user, router]);

  return (
    <div className="text-sm text-neutral-500">Redirecting to your dashboard…</div>
  );
}
