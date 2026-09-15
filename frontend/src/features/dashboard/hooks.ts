"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { AdminDashboardStats, TeacherDashboardStats } from "@/lib/api/types";

export function useAdminStats() {
  return useQuery({
    queryKey: ["dashboard", "admin"],
    queryFn: async () => {
      const { data } = await api.get<AdminDashboardStats>(endpoints.dashboard.admin);
      return data;
    },
  });
}

export function useTeacherStats() {
  return useQuery({
    queryKey: ["dashboard", "teacher"],
    queryFn: async () => {
      const { data } = await api.get<TeacherDashboardStats>(
        endpoints.dashboard.teacher
      );
      return data;
    },
  });
}
