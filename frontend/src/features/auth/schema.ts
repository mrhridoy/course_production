import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(6, "Min 6 characters"),
});

export const registerSchema = z.object({
  full_name: z.string().min(2, "Required"),
  email: z.string().email("Enter a valid email"),
  phone: z.string().optional().or(z.literal("")),
  password: z.string().min(6, "Min 6 characters"),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
