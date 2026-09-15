"use client";

import Link from "next/link";
import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ConfirmButton } from "@/components/shared/ConfirmButton";
import { useAllCourses, useDeleteCourse } from "@/features/courses/mutations";
import { useAuthStore } from "@/features/auth/store";
import { formatBDT, formatDate } from "@/lib/format";
import { extractApiError } from "@/lib/api/client";

export default function TeacherCoursesPage() {
  return (
    <RoleGuard allow={["teacher", "admin"]}>
      <TeacherCourses />
    </RoleGuard>
  );
}

function TeacherCourses() {
  const user = useAuthStore((s) => s.user);
  const { data, isLoading } = useAllCourses({ limit: 200 });
  const del = useDeleteCourse();

  const myCourses =
    user?.role === "admin"
      ? data ?? []
      : (data ?? []).filter((c) => c.teacher?.id === user?.id);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {user?.role === "admin" ? "All courses" : "My courses"}
          </h1>
          <p className="mt-1 text-sm text-neutral-600">
            {myCourses.length} {myCourses.length === 1 ? "course" : "courses"}
          </p>
        </div>
        <Link href="/dashboard/teacher/courses/new">
          <Button>+ New course</Button>
        </Link>
      </div>

      <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
            <tr>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Level</th>
              <th className="px-4 py-3">Price</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Updated</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-100">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-neutral-500">
                  Loading…
                </td>
              </tr>
            ) : myCourses.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-neutral-500">
                  No courses yet —{" "}
                  <Link
                    href="/dashboard/teacher/courses/new"
                    className="text-brand-600 hover:underline"
                  >
                    create your first one
                  </Link>
                  .
                </td>
              </tr>
            ) : (
              myCourses.map((c) => (
                <tr key={c.id} className="hover:bg-neutral-50">
                  <td className="px-4 py-3">
                    <Link
                      href={`/dashboard/teacher/courses/${c.id}/edit`}
                      className="font-medium text-neutral-900 hover:text-brand-600"
                    >
                      {c.title}
                    </Link>
                    {c.category && (
                      <p className="text-xs text-neutral-500">{c.category.name}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 capitalize text-neutral-700">{c.level}</td>
                  <td className="px-4 py-3">{c.price > 0 ? formatBDT(c.price) : "Free"}</td>
                  <td className="px-4 py-3">
                    {c.is_published ? (
                      <Badge variant="success">Published</Badge>
                    ) : (
                      <Badge variant="warning">Draft</Badge>
                    )}
                  </td>
                  <td className="px-4 py-3 text-neutral-600">
                    {formatDate(c.updated_at ?? c.created_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="inline-flex gap-2">
                      <Link href={`/dashboard/teacher/courses/${c.id}/edit`}>
                        <Button variant="outline" size="sm">
                          Edit
                        </Button>
                      </Link>
                      <ConfirmButton
                        variant="ghost"
                        size="sm"
                        message={`Delete "${c.title}"? This cannot be undone.`}
                        onConfirm={() =>
                          del.mutate(c.id, {
                            onSuccess: () => toast.success("Course deleted"),
                            onError: (err) => toast.error(extractApiError(err)),
                          })
                        }
                      >
                        Delete
                      </ConfirmButton>
                    </div>
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
