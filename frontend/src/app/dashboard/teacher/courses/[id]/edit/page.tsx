"use client";

import { use } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CourseForm } from "@/components/dashboard/CourseForm";
import { ThumbnailUploader } from "@/components/dashboard/ThumbnailUploader";
import { useCourse } from "@/features/courses/hooks";
import { useUpdateCourse } from "@/features/courses/mutations";
import { extractApiError } from "@/lib/api/client";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EditCoursePage({ params }: PageProps) {
  const { id } = use(params);
  const courseId = Number(id);

  return (
    <RoleGuard allow={["teacher", "admin"]}>
      <EditCourse courseId={courseId} />
    </RoleGuard>
  );
}

function EditCourse({ courseId }: { courseId: number }) {
  const { data: course, isLoading } = useCourse(courseId);
  const update = useUpdateCourse();

  if (isLoading) {
    return <p className="text-sm text-neutral-500">Loading…</p>;
  }
  if (!course) {
    return <p className="text-sm text-red-600">Course not found.</p>;
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <nav className="text-sm text-neutral-500">
        <Link href="/dashboard/teacher/courses" className="hover:text-neutral-900">
          ← All courses
        </Link>
      </nav>

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Edit course</CardTitle>
          </CardHeader>
          <CardContent>
            <CourseForm
              submitLabel="Save changes"
              isPending={update.isPending}
              defaultValues={{
                title: course.title,
                description: course.description ?? "",
                promo_video_url: course.promo_video_url ?? "",
                price: course.price,
                duration_hours: course.duration_hours ?? "",
                level: course.level,
                is_published: course.is_published,
                category_id: course.category?.id ?? "",
              }}
              onSubmit={(input) =>
                update.mutate(
                  { id: courseId, input },
                  {
                    onSuccess: () => toast.success("Course updated"),
                    onError: (err) => toast.error(extractApiError(err)),
                  }
                )
              }
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Thumbnail</CardTitle>
          </CardHeader>
          <CardContent>
            <ThumbnailUploader
              courseId={courseId}
              currentUrl={course.thumbnail_url}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
