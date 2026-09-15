import "server-only";
import type { Course } from "@/lib/api/types";

// API_URL is a server-only env var pointing to the internal Docker service.
// Falls back to NEXT_PUBLIC_API_URL (public domain) for local dev.
const baseURL = `${
  process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
}${process.env.NEXT_PUBLIC_API_BASE_PATH ?? "/api/v1"}`;

export async function fetchCourses(params?: {
  skip?: number;
  limit?: number;
}): Promise<Course[]> {
  const url = new URL(`${baseURL}/courses/`);
  if (params?.skip != null) url.searchParams.set("skip", String(params.skip));
  if (params?.limit != null) url.searchParams.set("limit", String(params.limit));

  const res = await fetch(url.toString(), {
    next: { revalidate: 60, tags: ["courses"] },
  });
  if (!res.ok) throw new Error(`Failed to load courses (${res.status})`);
  return (await res.json()) as Course[];
}

export async function fetchCourseById(id: number): Promise<Course | null> {
  const res = await fetch(`${baseURL}/courses/${id}`, {
    next: { revalidate: 60, tags: [`course:${id}`] },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Failed to load course (${res.status})`);
  return (await res.json()) as Course;
}
