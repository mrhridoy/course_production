"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Enrollment } from "@/lib/api/types";

export function useMyEnrollments() {
  return useQuery({
    queryKey: ["enrollments", "my"],
    queryFn: async () => {
      const { data } = await api.get<Enrollment[]>(endpoints.enrollments.my);
      return data;
    },
  });
}

export function useEnroll() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (course_id: number) => {
      const { data } = await api.post<Enrollment>(endpoints.enrollments.listAll, {
        course_id,
      });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["enrollments", "my"] });
    },
  });
}
