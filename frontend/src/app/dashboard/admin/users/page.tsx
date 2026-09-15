"use client";

import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { ConfirmButton } from "@/components/shared/ConfirmButton";
import {
  useAssignRole,
  useDeleteUser,
  useToggleActive,
  useUsers,
} from "@/features/users/hooks";
import { useAuthStore } from "@/features/auth/store";
import type { UserRole } from "@/lib/api/types";
import { extractApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/format";

export default function AdminUsersPage() {
  return (
    <RoleGuard allow={["admin"]}>
      <UsersAdmin />
    </RoleGuard>
  );
}

function UsersAdmin() {
  const me = useAuthStore((s) => s.user);
  const { data: users, isLoading } = useUsers({ limit: 200 });
  const assignRole = useAssignRole();
  const toggleActive = useToggleActive();
  const del = useDeleteUser();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Users</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Manage user roles and access.
        </p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
            <tr>
              <th className="px-4 py-3">User</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Joined</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-neutral-500">
                  Loading…
                </td>
              </tr>
            ) : !users || users.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-neutral-500">
                  No users.
                </td>
              </tr>
            ) : (
              users.map((u) => {
                const isMe = me?.id === u.id;
                return (
                  <tr key={u.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3">
                      <div className="font-medium">{u.full_name}</div>
                      <div className="text-xs text-neutral-500">{u.email}</div>
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        className="h-8 w-32"
                        value={u.role}
                        disabled={isMe || assignRole.isPending}
                        onChange={(e) =>
                          assignRole.mutate(
                            { id: u.id, role: e.target.value as UserRole },
                            {
                              onSuccess: () => toast.success("Role updated"),
                              onError: (err) => toast.error(extractApiError(err)),
                            }
                          )
                        }
                      >
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                        <option value="admin">Admin</option>
                      </Select>
                    </td>
                    <td className="px-4 py-3">
                      {u.is_active ? (
                        <Badge variant="success">Active</Badge>
                      ) : (
                        <Badge variant="neutral">Disabled</Badge>
                      )}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="inline-flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={isMe || toggleActive.isPending}
                          onClick={() =>
                            toggleActive.mutate(u.id, {
                              onSuccess: () => toast.success("Status updated"),
                              onError: (err) => toast.error(extractApiError(err)),
                            })
                          }
                        >
                          {u.is_active ? "Disable" : "Enable"}
                        </Button>
                        <ConfirmButton
                          size="sm"
                          variant="ghost"
                          disabled={isMe}
                          message={`Delete user "${u.full_name}"?`}
                          onConfirm={() =>
                            del.mutate(u.id, {
                              onSuccess: () => toast.success("User deleted"),
                              onError: (err) => toast.error(extractApiError(err)),
                            })
                          }
                        >
                          Delete
                        </ConfirmButton>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
