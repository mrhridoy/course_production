"use client";

import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { useAllPayments, useUpdatePaymentStatus } from "@/features/payments/hooks";
import type { PaymentStatus } from "@/lib/api/types";
import { extractApiError } from "@/lib/api/client";
import { formatBDT, formatDate } from "@/lib/format";

export default function AdminPaymentsPage() {
  return (
    <RoleGuard allow={["admin"]}>
      <PaymentsAdmin />
    </RoleGuard>
  );
}

function PaymentsAdmin() {
  const { data: payments, isLoading } = useAllPayments({ limit: 200 });
  const updateStatus = useUpdatePaymentStatus();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Payments</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Review and verify student payments.
        </p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Course</th>
              <th className="px-4 py-3">Student</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Method</th>
              <th className="px-4 py-3">Txn</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Created</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? (
              <tr>
                <td colSpan={9} className="px-4 py-10 text-center text-neutral-500">
                  Loading…
                </td>
              </tr>
            ) : !payments || payments.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-10 text-center text-neutral-500">
                  No payments yet.
                </td>
              </tr>
            ) : (
              payments.map((p) => (
                <tr key={p.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3 font-mono text-xs">#{p.id}</td>
                  <td className="px-4 py-3">#{p.course_id}</td>
                  <td className="px-4 py-3">#{p.student_id}</td>
                  <td className="px-4 py-3">{formatBDT(p.amount)}</td>
                  <td className="px-4 py-3 capitalize">{p.method}</td>
                  <td className="px-4 py-3 font-mono text-xs">
                    {p.transaction_id ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <PaymentStatusBadge status={p.status} />
                  </td>
                  <td className="px-4 py-3 text-neutral-600">
                    {formatDate(p.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Select
                      className="h-8 w-36"
                      value={p.status}
                      disabled={updateStatus.isPending}
                      onChange={(e) =>
                        updateStatus.mutate(
                          { id: p.id, status: e.target.value as PaymentStatus },
                          {
                            onSuccess: () => toast.success("Status updated"),
                            onError: (err) => toast.error(extractApiError(err)),
                          }
                        )
                      }
                    >
                      <option value="pending">Pending</option>
                      <option value="completed">Completed</option>
                      <option value="failed">Failed</option>
                      <option value="refunded">Refunded</option>
                    </Select>
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

function PaymentStatusBadge({ status }: { status: PaymentStatus }) {
  const map = {
    pending: { variant: "warning" as const, label: "Pending" },
    completed: { variant: "success" as const, label: "Completed" },
    failed: { variant: "danger" as const, label: "Failed" },
    refunded: { variant: "info" as const, label: "Refunded" },
  };
  const { variant, label } = map[status];
  return <Badge variant={variant}>{label}</Badge>;
}
