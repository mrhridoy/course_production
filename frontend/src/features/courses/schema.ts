import { z } from "zod";

export const courseLevelEnum = z.enum(["beginner", "intermediate", "advanced"]);

export const courseSchema = z.object({
  title: z.string().min(2, "Title is required"),
  description: z.string().optional().or(z.literal("")),
  promo_video_url: z
    .string()
    .url("Must be a valid URL")
    .optional()
    .or(z.literal("")),
  price: z.coerce.number().min(0, "Price must be ≥ 0").default(0),
  duration_hours: z.coerce
    .number()
    .min(0, "Duration must be ≥ 0")
    .optional()
    .or(z.literal("")),
  level: courseLevelEnum.default("beginner"),
  is_published: z.boolean().default(false),
  category_id: z.coerce.number().int().positive().optional().or(z.literal("")),
});

export type CourseFormInput = z.input<typeof courseSchema>;
export type CourseFormOutput = z.output<typeof courseSchema>;
