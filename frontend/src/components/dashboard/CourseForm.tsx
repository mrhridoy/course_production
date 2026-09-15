"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { useCategories } from "@/features/categories/hooks";
import { courseSchema, type CourseFormInput } from "@/features/courses/schema";
import type { CourseInput } from "@/features/courses/mutations";

interface Props {
  defaultValues?: Partial<CourseFormInput>;
  submitLabel: string;
  isPending?: boolean;
  onSubmit: (data: CourseInput) => void;
}

export function CourseForm({
  defaultValues,
  submitLabel,
  isPending,
  onSubmit,
}: Props) {
  const { data: categories } = useCategories();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CourseFormInput>({
    resolver: zodResolver(courseSchema),
    defaultValues: {
      title: "",
      description: "",
      promo_video_url: "",
      price: 0,
      duration_hours: "",
      level: "beginner",
      is_published: false,
      category_id: "",
      ...defaultValues,
    },
  });

  const submit = handleSubmit((values) => {
    const payload: CourseInput = {
      title: values.title,
      description: values.description ? String(values.description) : null,
      promo_video_url: values.promo_video_url ? String(values.promo_video_url) : null,
      price: Number(values.price ?? 0),
      duration_hours:
        values.duration_hours === "" || values.duration_hours == null
          ? null
          : Number(values.duration_hours),
      level: values.level,
      is_published: Boolean(values.is_published),
      category_id:
        values.category_id === "" || values.category_id == null
          ? null
          : Number(values.category_id),
    };
    onSubmit(payload);
  });

  return (
    <form onSubmit={submit} className="space-y-5">
      <Field label="Title" error={errors.title?.message}>
        <Input {...register("title")} />
      </Field>

      <Field label="Description" error={errors.description?.message}>
        <Textarea rows={6} {...register("description")} />
      </Field>

      <div className="grid gap-5 md:grid-cols-2">
        <Field label="Price (BDT)" error={errors.price?.message}>
          <Input type="number" step="1" min={0} {...register("price")} />
        </Field>
        <Field label="Duration (hours)" error={errors.duration_hours?.message}>
          <Input type="number" step="0.5" min={0} {...register("duration_hours")} />
        </Field>
        <Field label="Level" error={errors.level?.message}>
          <Select {...register("level")}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </Select>
        </Field>
        <Field label="Category" error={errors.category_id?.message}>
          <Select {...register("category_id")}>
            <option value="">Uncategorized</option>
            {categories?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </Field>
      </div>

      <Field label="Promo video URL" error={errors.promo_video_url?.message}>
        <Input
          type="url"
          placeholder="https://youtube.com/…"
          {...register("promo_video_url")}
        />
      </Field>

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          className="size-4 rounded border-neutral-300 text-brand-600 focus:ring-brand-500"
          {...register("is_published")}
        />
        <span className="text-sm">Publish course</span>
      </label>

      <div className="pt-2">
        <Button type="submit" disabled={isPending}>
          {isPending ? "Saving…" : submitLabel}
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
