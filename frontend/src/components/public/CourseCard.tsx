import Image from "next/image";
import Link from "next/link";
import type { Course } from "@/lib/api/types";
import { formatBDT, resolveMediaUrl } from "@/lib/format";

export function CourseCard({ course }: { course: Course }) {
  return (
    <Link
      href={`/courses/${course.id}`}
      className="group block overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm transition hover:shadow-md"
    >
      <div className="relative aspect-video w-full bg-neutral-100">
        {resolveMediaUrl(course.thumbnail_url) ? (
          <Image
            src={resolveMediaUrl(course.thumbnail_url)!}
            alt={course.title}
            fill
            sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
            className="object-cover transition group-hover:scale-[1.02]"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-neutral-400">
            No image
          </div>
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <span className="capitalize">{course.level}</span>
          {course.category && <span>{course.category.name}</span>}
        </div>
        <h3 className="line-clamp-2 text-sm font-semibold text-neutral-900">
          {course.title}
        </h3>
        {course.description && (
          <p className="line-clamp-2 text-xs text-neutral-600">{course.description}</p>
        )}
        <div className="flex items-center justify-between pt-1">
          <span className="text-sm font-semibold text-brand-600">
            {course.price > 0 ? formatBDT(course.price) : "Free"}
          </span>
          {course.duration_hours && (
            <span className="text-xs text-neutral-500">{course.duration_hours}h</span>
          )}
        </div>
      </div>
    </Link>
  );
}
