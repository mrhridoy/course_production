import type { MetadataRoute } from "next";
import { SITE } from "@/lib/seo";
import { fetchCourses } from "@/features/courses/server";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticUrls: MetadataRoute.Sitemap = [
    { url: `${SITE.url}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE.url}/courses`, changeFrequency: "daily", priority: 0.8 },
  ];

  const courses = await fetchCourses({ limit: 200 }).catch(() => []);
  const courseUrls: MetadataRoute.Sitemap = courses.map((c) => ({
    url: `${SITE.url}/courses/${c.id}`,
    lastModified: c.updated_at ?? c.created_at,
    changeFrequency: "weekly",
    priority: 0.6,
  }));

  return [...staticUrls, ...courseUrls];
}
