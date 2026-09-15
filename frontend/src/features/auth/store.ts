"use client";

import { create } from "zustand";
import type { User } from "@/lib/api/types";
import { tokenStorage } from "@/lib/auth/storage";

interface AuthState {
  user: User | null;
  isHydrated: boolean;
  hydrate: () => void;
  setSession: (user: User, accessToken: string, refreshToken: string) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isHydrated: false,
  hydrate: () => {
    const user = tokenStorage.getUser<User>();
    set({ user, isHydrated: true });
  },
  setSession: (user, accessToken, refreshToken) => {
    tokenStorage.set(accessToken, refreshToken, user);
    set({ user, isHydrated: true });
  },
  clearSession: () => {
    tokenStorage.clear();
    set({ user: null });
  },
}));
