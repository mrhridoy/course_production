import { CourseCard } from "@/components/public/CourseCard";
import { fetchCourses } from "@/features/courses/server";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Courses",
  description: "Browse all online courses available on ICT Bangladesh.",
  path: "/courses",
});

export const revalidate = 60;

export default async function CoursesPage() {
  const courses = await fetchCourses({ limit: 60 }).catch(() => []);

  return (
    <section className="mx-auto max-w-7xl px-4 py-10">
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight">All courses</h1>
        <p className="mt-1 text-sm text-neutral-600">
          {courses.length} {courses.length === 1 ? "course" : "courses"} available
        </p>
      </header>

      {courses.length === 0 ? (
        <div className="rounded-xl border border-dashed border-neutral-300 bg-neutral-50 p-10 text-center text-sm text-neutral-600">
          No courses are published yet. Check back soon.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((c) => (
            <CourseCard key={c.id} course={c} />
          ))}
        </div>
      )}
    </section>
  );
}
