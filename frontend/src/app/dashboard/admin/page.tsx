"use client";

import { RoleGuard } from "@/lib/auth/guards";
import { StatCard } from "@/components/dashboard/StatCard";
import { useAdminStats } from "@/features/dashboard/hooks";
import { formatBDT } from "@/lib/format";

export default function AdminDashboardPage() {
  return (
    <RoleGuard allow={["admin"]}>
      <AdminOverview />
    </RoleGuard>
  );
}

function AdminOverview() {
  const { data, isLoading } = useAdminStats();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Admin overview</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Platform-wide stats and quick links.
        </p>
      </div>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Users & courses
        </h2>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Total users" value={fmt(isLoading, data?.total_users)} />
          <StatCard label="Students" value={fmt(isLoading, data?.total_students)} />
          <StatCard label="Teachers" value={fmt(isLoading, data?.total_teachers)} />
          <StatCard label="Total courses" value={fmt(isLoading, data?.total_courses)} />
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-neutral-500">
          Activity
        </h2>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard
            label="Published courses"
            value={fmt(isLoading, data?.published_courses)}
          />
          <StatCard
            label="Enrollments"
            value={fmt(isLoading, data?.total_enrollments)}
          />
          <StatCard
            label="Total revenue"
            value={isLoading ? "…" : formatBDT(data?.total_revenue ?? 0)}
          />
          <StatCard
            label="Pending payments"
            value={fmt(isLoading, data?.pending_payments)}
            hint="Awaiting verification"
          />
        </div>
      </section>
    </div>
  );
}

function fmt(loading: boolean, n?: number) {
  return loading ? "…" : n ?? 0;
}
