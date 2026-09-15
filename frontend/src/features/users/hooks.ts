"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { User, UserRole } from "@/lib/api/types";

const KEY = ["users"] as const;

export function useUsers(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...KEY, params],
    queryFn: async () => {
      const { data } = await api.get<User[]>(endpoints.users.list, { params });
      return data;
    },
  });
}

export function useAssignRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, role }: { id: number; role: UserRole }) => {
      const { data } = await api.put<User>(endpoints.users.role(id), { role });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useToggleActive() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await api.patch<User>(endpoints.users.toggleActive(id));
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useDeleteUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(endpoints.users.byId(id));
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}
