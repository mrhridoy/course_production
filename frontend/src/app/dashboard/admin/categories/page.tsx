"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ConfirmButton } from "@/components/shared/ConfirmButton";
import {
  useCategories,
  useCreateCategory,
  useDeleteCategory,
  useUpdateCategory,
} from "@/features/categories/hooks";
import type { Category } from "@/lib/api/types";
import { extractApiError } from "@/lib/api/client";
import { formatDate } from "@/lib/format";

const schema = z.object({
  name: z.string().min(2, "Required"),
  description: z.string().optional().or(z.literal("")),
});
type FormInput = z.infer<typeof schema>;

export default function AdminCategoriesPage() {
  return (
    <RoleGuard allow={["admin"]}>
      <CategoriesAdmin />
    </RoleGuard>
  );
}

function CategoriesAdmin() {
  const { data: categories, isLoading } = useCategories();
  const create = useCreateCategory();
  const del = useDeleteCategory();
  const [editing, setEditing] = useState<Category | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormInput>({ resolver: zodResolver(schema) });

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
        <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Slug</th>
                <th className="px-4 py-3">Created</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="px-4 py-10 text-center text-neutral-500">
                    Loading…
                  </td>
                </tr>
              ) : !categories || categories.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-10 text-center text-neutral-500">
                    No categories yet.
                  </td>
                </tr>
              ) : (
                categories.map((c) => (
                  <tr key={c.id} className="hover:bg-neutral-50">
                    <td className="px-4 py-3 font-medium">{c.name}</td>
                    <td className="px-4 py-3 text-neutral-500">{c.slug}</td>
                    <td className="px-4 py-3 text-neutral-600">
                      {formatDate(c.created_at)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="inline-flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditing(c)}
                        >
                          Edit
                        </Button>
                        <ConfirmButton
                          size="sm"
                          variant="ghost"
                          message={`Delete "${c.name}"?`}
                          onConfirm={() =>
                            del.mutate(c.id, {
                              onSuccess: () => toast.success("Category deleted"),
                              onError: (err) => toast.error(extractApiError(err)),
                            })
                          }
                        >
                          Delete
                        </ConfirmButton>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{editing ? `Edit "${editing.name}"` : "New category"}</CardTitle>
        </CardHeader>
        <CardContent>
          {editing ? (
            <EditForm
              category={editing}
              onDone={() => {
                setEditing(null);
                reset();
              }}
            />
          ) : (
            <form
              onSubmit={handleSubmit((values) =>
                create.mutate(
                  { name: values.name, description: values.description || undefined },
                  {
                    onSuccess: () => {
                      toast.success("Category created");
                      reset();
                    },
                    onError: (err) => toast.error(extractApiError(err)),
                  }
                )
              )}
              className="space-y-4"
            >
              <div className="space-y-1.5">
                <Label htmlFor="name">Name</Label>
                <Input id="name" {...register("name")} />
                {errors.name && (
                  <p className="text-xs text-red-600">{errors.name.message}</p>
                )}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" rows={3} {...register("description")} />
              </div>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending ? "Creating…" : "Create category"}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function EditForm({ category, onDone }: { category: Category; onDone: () => void }) {
  const update = useUpdateCategory();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormInput>({
    resolver: zodResolver(schema),
    defaultValues: { name: category.name, description: category.description ?? "" },
  });

  return (
    <form
      onSubmit={handleSubmit((values) =>
        update.mutate(
          {
            id: category.id,
            input: { name: values.name, description: values.description || undefined },
          },
          {
            onSuccess: () => {
              toast.success("Category updated");
              onDone();
            },
            onError: (err) => toast.error(extractApiError(err)),
          }
        )
      )}
      className="space-y-4"
    >
      <div className="space-y-1.5">
        <Label htmlFor="edit-name">Name</Label>
        <Input id="edit-name" {...register("name")} />
        {errors.name && <p className="text-xs text-red-600">{errors.name.message}</p>}
      </div>
      <div className="space-y-1.5">
        <Label htmlFor="edit-description">Description</Label>
        <Textarea id="edit-description" rows={3} {...register("description")} />
      </div>
      <div className="flex gap-2">
        <Button type="submit" disabled={update.isPending}>
          {update.isPending ? "Saving…" : "Save changes"}
        </Button>
        <Button type="button" variant="ghost" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
