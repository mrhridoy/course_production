"use client";

import { Suspense, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import Link from "next/link";
import { RoleGuard } from "@/lib/auth/guards";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useEnroll, useMyEnrollments } from "@/features/enrollments/hooks";
import { useCourse } from "@/features/courses/hooks";
import { extractApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/format";

export default function StudentDashboardPage() {
  return (
    <RoleGuard allow={["student", "admin"]}>
      <Suspense>
        <StudentDashboard />
      </Suspense>
    </RoleGuard>
  );
}

function StudentDashboard() {
  const params = useSearchParams();
  const enrollParam = params.get("enroll");
  const enrollCourseId = enrollParam ? Number(enrollParam) : null;

  const { data: enrollments, isLoading, error } = useMyEnrollments();
  const enroll = useEnroll();

  useEffect(() => {
    if (!enrollCourseId || enroll.isPending || enroll.isSuccess) return;
    enroll.mutate(enrollCourseId, {
      onSuccess: () => toast.success("Enrolled successfully"),
      onError: (err) => toast.error(extractApiError(err)),
    });
  }, [enrollCourseId, enroll]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">My enrollments</h1>
        <p className="mt-1 text-sm text-neutral-600">
          Courses you&apos;ve enrolled in.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : error ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-sm font-medium text-red-600">
              Could not load enrollments
            </p>
            <p className="mt-1 text-xs text-neutral-500">
              {extractApiError(error)}
            </p>
          </CardContent>
        </Card>
      ) : !enrollments || enrollments.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
            <p className="text-sm text-neutral-600">
              You haven&apos;t enrolled in any courses yet.
            </p>
            <Link href="/courses">
              <Button>Browse courses</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {enrollments.map((e) => (
            <EnrollmentCard
              key={e.id}
              courseId={e.course_id}
              status={e.status}
              enrolledAt={e.enrolled_at}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function EnrollmentCard({
  courseId,
  status,
  enrolledAt,
}: {
  courseId: number;
  status: string;
  enrolledAt: string;
}) {
  const { data: course } = useCourse(courseId);
  return (
    <Card>
      <CardHeader>
        <CardTitle className="line-clamp-1">
          {course?.title ?? `Course #${courseId}`}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between text-xs">
          <span
            className={`rounded-full px-2 py-1 capitalize ${
              status === "active"
                ? "bg-green-50 text-green-700"
                : status === "completed"
                  ? "bg-blue-50 text-blue-700"
                  : "bg-neutral-100 text-neutral-600"
            }`}
          >
            {status}
          </span>
          <span className="text-neutral-500">Enrolled {formatDate(enrolledAt)}</span>
        </div>
        <Link href={`/courses/${courseId}`}>
          <Button variant="outline" size="sm" className="w-full">
            View course
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
