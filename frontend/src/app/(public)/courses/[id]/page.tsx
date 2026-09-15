import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchCourseById } from "@/features/courses/server";
import { CourseEnrollButton } from "@/components/public/CourseEnrollButton";
import { formatBDT } from "@/lib/format";
import { buildMetadata } from "@/lib/seo";

export const revalidate = 60;

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const course = await fetchCourseById(Number(id)).catch(() => null);
  if (!course) return buildMetadata({ title: "Course not found" });
  return buildMetadata({
    title: course.title,
    description: course.description ?? undefined,
    path: `/courses/${course.id}`,
    image: course.thumbnail_url ?? undefined,
  });
}

export default async function CourseDetailPage({ params }: Props) {
  const { id } = await params;
  const course = await fetchCourseById(Number(id));
  if (!course) notFound();

  return (
    <section className="mx-auto max-w-5xl px-4 py-10">
      <nav className="mb-6 text-sm text-neutral-500">
        <Link href="/courses" className="hover:text-neutral-900">
          ← All courses
        </Link>
      </nav>

      <div className="grid gap-8 md:grid-cols-[2fr_1fr]">
        <div>
          {course.thumbnail_url && (
            <div className="relative mb-6 aspect-video overflow-hidden rounded-xl bg-neutral-100">
              <Image
                src={course.thumbnail_url}
                alt={course.title}
                fill
                className="object-cover"
                priority
              />
            </div>
          )}
          <div className="flex items-center gap-2 text-xs">
            <span className="rounded-full bg-brand-50 px-2 py-1 capitalize text-brand-700">
              {course.level}
            </span>
            {course.category && (
              <span className="rounded-full bg-neutral-100 px-2 py-1 text-neutral-700">
                {course.category.name}
              </span>
            )}
          </div>
          <h1 className="mt-3 text-3xl font-bold tracking-tight">{course.title}</h1>
          {course.description && (
            <p className="mt-4 whitespace-pre-line leading-relaxed text-neutral-700">
              {course.description}
            </p>
          )}
        </div>

        <aside className="space-y-4 rounded-xl border border-neutral-200 bg-white p-5 shadow-sm md:sticky md:top-20 md:self-start">
          <div className="text-3xl font-bold text-brand-600">
            {course.price > 0 ? formatBDT(course.price) : "Free"}
          </div>
          {course.duration_hours && (
            <p className="text-sm text-neutral-600">
              Duration: <strong>{course.duration_hours} hours</strong>
            </p>
          )}
          {course.teacher && (
            <p className="text-sm text-neutral-600">
              Instructor: <strong>{course.teacher.full_name}</strong>
            </p>
          )}
          <CourseEnrollButton courseId={course.id} price={course.price} />
        </aside>
      </div>
    </section>
  );
}
