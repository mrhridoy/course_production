"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Course, CourseLevel } from "@/lib/api/types";

export interface CourseInput {
  title: string;
  description?: string | null;
  promo_video_url?: string | null;
  price?: number;
  duration_hours?: number | null;
  level?: CourseLevel;
  is_published?: boolean;
  category_id?: number | null;
}

export function useAllCourses(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ["courses", "all", params],
    queryFn: async () => {
      const { data } = await api.get<Course[]>(endpoints.courses.listAll, { params });
      return data;
    },
  });
}

export function useCreateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: CourseInput) => {
      const { data } = await api.post<Course>(endpoints.courses.list, input);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["courses"] });
    },
  });
}

export function useUpdateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, input }: { id: number; input: Partial<CourseInput> }) => {
      const { data } = await api.put<Course>(endpoints.courses.byId(id), input);
      return data;
    },
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      qc.invalidateQueries({ queryKey: ["course", variables.id] });
    },
  });
}

export function useDeleteCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(endpoints.courses.byId(id));
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });
}

export function useUploadThumbnail() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, file }: { id: number; file: File }) => {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post(endpoints.courses.thumbnail(id), fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      qc.invalidateQueries({ queryKey: ["course", variables.id] });
    },
  });
}
