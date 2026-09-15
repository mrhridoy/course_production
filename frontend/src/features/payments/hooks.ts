"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api/client";
import { endpoints } from "@/lib/api/endpoints";
import type { Payment, PaymentMethod, PaymentStatus } from "@/lib/api/types";

const KEY = ["payments"] as const;

export function useMyPayments() {
  return useQuery({
    queryKey: [...KEY, "my"],
    queryFn: async () => {
      const { data } = await api.get<Payment[]>(endpoints.payments.my);
      return data;
    },
  });
}

export function useAllPayments(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: [...KEY, "all", params],
    queryFn: async () => {
      const { data } = await api.get<Payment[]>(endpoints.payments.listAll, { params });
      return data;
    },
  });
}

export function useCreatePayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      course_id: number;
      amount: number;
      method: PaymentMethod;
      transaction_id?: string;
      note?: string;
    }) => {
      const { data } = await api.post<Payment>(endpoints.payments.listAll, input);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}

export function useUpdatePaymentStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      status,
      transaction_id,
      note,
    }: {
      id: number;
      status: PaymentStatus;
      transaction_id?: string;
      note?: string;
    }) => {
      const { data } = await api.put<Payment>(endpoints.payments.status(id), {
        status,
        transaction_id,
        note,
      });
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
}
