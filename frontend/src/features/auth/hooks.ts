"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { AuthTokens, User } from "@/lib/api/types";
import type { LoginInput, RegisterInput } from "./schema";
import { useAuthStore } from "./store";

export function useLogin() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: async (input: LoginInput) => {
      const { data } = await api.post<AuthTokens>(endpoints.auth.login, input);
      return data;
    },
    onSuccess: (data) => {
      setSession(data.user, data.access_token, data.refresh_token);
    },
  });
}

export function useRegister() {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: async (input: RegisterInput) => {
      const payload = { ...input, phone: input.phone || undefined };
      const { data } = await api.post<AuthTokens>(endpoints.auth.register, payload);
      return data;
    },
    onSuccess: (data) => {
      setSession(data.user, data.access_token, data.refresh_token);
    },
  });
}

export function useMe(enabled = true) {
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const { data } = await api.get<User>(endpoints.auth.me);
      return data;
    },
    enabled,
    staleTime: 60_000,
  });
}

export function useLogout() {
  const clear = useAuthStore((s) => s.clearSession);
  const qc = useQueryClient();
  return () => {
    clear();
    qc.clear();
  };
}
