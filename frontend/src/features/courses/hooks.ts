"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Course } from "@/lib/api/types";

export function useCourse(id: number | null) {
  return useQuery({
    queryKey: ["course", id],
    queryFn: async () => {
      const { data } = await api.get<Course>(endpoints.courses.byId(id as number));
      return data;
    },
    enabled: id != null,
  });
}

export function useCourses(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ["courses", params],
    queryFn: async () => {
      const { data } = await api.get<Course[]>(endpoints.courses.list, { params });
      return data;
    },
  });
}
