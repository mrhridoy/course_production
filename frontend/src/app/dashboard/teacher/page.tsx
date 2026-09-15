"use client";

import Link from "next/link";
import { RoleGuard } from "@/lib/auth/guards";
import { StatCard } from "@/components/dashboard/StatCard";
import { Button } from "@/components/ui/button";
import { useTeacherStats } from "@/features/dashboard/hooks";
import { formatBDT } from "@/lib/format";

export default function TeacherDashboardPage() {
  return (
    <RoleGuard allow={["teacher", "admin"]}>
      <TeacherOverview />
    </RoleGuard>
  );
}

function TeacherOverview() {
  const { data, isLoading } = useTeacherStats();

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Teacher dashboard</h1>
          <p className="mt-1 text-sm text-neutral-600">Overview of your courses.</p>
        </div>
        <Link href="/dashboard/teacher/courses/new">
          <Button>+ New course</Button>
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total courses" value={isLoading ? "…" : data?.total_courses ?? 0} />
        <StatCard
          label="Published"
          value={isLoading ? "…" : data?.published_courses ?? 0}
        />
        <StatCard
          label="Enrollments"
          value={isLoading ? "…" : data?.total_enrollments ?? 0}
        />
        <StatCard
          label="Revenue"
          value={isLoading ? "…" : formatBDT(data?.total_revenue ?? 0)}
        />
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-6">
        <h2 className="text-base font-semibold">Quick actions</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link href="/dashboard/teacher/courses">
            <Button variant="outline">Manage my courses</Button>
          </Link>
          <Link href="/dashboard/teacher/courses/new">
            <Button variant="outline">Create new course</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
