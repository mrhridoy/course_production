"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Category } from "@/lib/api/types";

const KEY = ["categories"] as const;

export function useCategories() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data } = await api.get<Category[]>(endpoints.categories.list);
      return data;
    },
    staleTime: 5 * 60_000,
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string; description?: string }) => {
      const { data } = await api.post<Category>(endpoints.categories.list, input);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useUpdateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      input,
    }: {
      id: number;
      input: { name?: string; description?: string };
    }) => {
      const { data } = await api.put<Category>(endpoints.categories.byId(id), input);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(endpoints.categories.byId(id));
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}
