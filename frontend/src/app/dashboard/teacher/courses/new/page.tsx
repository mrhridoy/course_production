"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CourseForm } from "@/components/dashboard/CourseForm";
import { useCreateCourse } from "@/features/courses/mutations";
import { extractApiError } from "@/lib/api/client";

export default function NewCoursePage() {
  return (
    <RoleGuard allow={["teacher", "admin"]}>
      <NewCourse />
    </RoleGuard>
  );
}

function NewCourse() {
  const router = useRouter();
  const create = useCreateCourse();

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <nav className="text-sm text-neutral-500">
        <Link href="/dashboard/teacher/courses" className="hover:text-neutral-900">
          ← All courses
        </Link>
      </nav>
      <Card>
        <CardHeader>
          <CardTitle>Create new course</CardTitle>
        </CardHeader>
        <CardContent>
          <CourseForm
            submitLabel="Create course"
            isPending={create.isPending}
            onSubmit={(input) =>
              create.mutate(input, {
                onSuccess: (course) => {
                  toast.success("Course created");
                  router.push(`/dashboard/teacher/courses/${course.id}/edit`);
                },
                onError: (err) => toast.error(extractApiError(err)),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
