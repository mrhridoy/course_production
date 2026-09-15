"use client";

import { RoleGuard } from "@/lib/auth/guards";
import { Badge } from "@/components/ui/badge";
import { useMyPayments } from "@/features/payments/hooks";
import type { PaymentStatus } from "@/lib/api/types";
import { formatBDT, formatDate } from "@/lib/format";

export default function StudentPaymentsPage() {
  return (
    <RoleGuard allow={["student", "admin"]}>
      <MyPayments />
    </RoleGuard>
  );
}

function MyPayments() {
  const { data: payments, isLoading } = useMyPayments();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My payments</h1>
        <p className="mt-1 text-sm text-neutral-600">All your transactions.</p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Course</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Method</th>
              <th className="px-4 py-3">Transaction</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-neutral-500">
                  Loading…
                </td>
              </tr>
            ) : !payments || payments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-neutral-500">
                  No payments yet.
                </td>
              </tr>
            ) : (
              payments.map((p) => (
                <tr key={p.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 text-neutral-600">
                    {formatDate(p.paid_at ?? p.created_at)}
                  </td>
                  <td className="px-4 py-3">Course #{p.course_id}</td>
                  <td className="px-4 py-3 font-medium">{formatBDT(p.amount)}</td>
                  <td className="px-4 py-3 capitalize">{p.method}</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {p.transaction_id ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <StatusPill status={p.status} />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status: PaymentStatus }) {
  const map = {
    pending: { variant: "warning" as const, label: "Pending" },
    completed: { variant: "success" as const, label: "Completed" },
    failed: { variant: "danger" as const, label: "Failed" },
    refunded: { variant: "info" as const, label: "Refunded" },
  };
  const { variant, label } = map[status];
  return <Badge variant={variant}>{label}</Badge>;
}
