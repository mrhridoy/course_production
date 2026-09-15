"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { RoleGuard } from "@/lib/auth/guards";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useCourse } from "@/features/courses/hooks";
import { useCreatePayment } from "@/features/payments/hooks";
import { useEnroll, useMyEnrollments } from "@/features/enrollments/hooks";
import type { PaymentMethod } from "@/lib/api/types";
import { extractApiError } from "@/lib/api/client";
import { formatBDT } from "@/lib/format";

const schema = z.object({
  method: z.enum(["bkash", "nagad", "card", "manual"]),
  transaction_id: z.string().min(4, "Enter the transaction ID").optional().or(z.literal("")),
  note: z.string().optional().or(z.literal("")),
});
type FormInput = z.infer<typeof schema>;

interface PageProps {
  params: Promise<{ courseId: string }>;
}

export default function CheckoutPage({ params }: PageProps) {
  const { courseId } = use(params);
  return (
    <RoleGuard allow={["student", "admin"]}>
      <Checkout courseId={Number(courseId)} />
    </RoleGuard>
  );
}

function Checkout({ courseId }: { courseId: number }) {
  const router = useRouter();
  const { data: course, isLoading } = useCourse(courseId);
  const { data: enrollments } = useMyEnrollments();
  const enroll = useEnroll();
  const pay = useCreatePayment();

  const isEnrolled = enrollments?.some((e) => e.course_id === courseId) ?? false;

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormInput>({
    resolver: zodResolver(schema),
    defaultValues: { method: "bkash", transaction_id: "", note: "" },
  });

  const method = watch("method");
  const isFree = course != null && course.price === 0;

  if (isLoading) {
    return <p className="text-sm text-neutral-500">Loading…</p>;
  }
  if (!course) {
    return <p className="text-sm text-red-600">Course not found.</p>;
  }
  if (isEnrolled) {
    return (
      <div className="mx-auto max-w-3xl space-y-4 text-center py-16">
        <p className="text-lg font-semibold text-green-700">
          ✓ You&apos;re already enrolled in this course.
        </p>
        <Link
          href="/dashboard/student"
          className="inline-block text-sm text-brand-600 underline"
        >
          Go to my courses →
        </Link>
      </div>
    );
  }

  const onFreeEnroll = () => {
    enroll.mutate(course.id, {
      onSuccess: () => {
        toast.success("Enrolled successfully");
        router.push("/dashboard/student");
      },
      onError: (err) => toast.error(extractApiError(err)),
    });
  };

  const onPay = handleSubmit((values) => {
    pay.mutate(
      {
        course_id: course.id,
        amount: course.price,
        method: values.method as PaymentMethod,
        transaction_id: values.transaction_id || undefined,
        note: values.note || undefined,
      },
      {
        onSuccess: () => {
          toast.success("Payment submitted — pending verification");
          router.push("/dashboard/student/payments");
        },
        onError: (err) => toast.error(extractApiError(err)),
      }
    );
  });

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <nav className="text-sm text-neutral-500">
        <Link href={`/courses/${course.id}`} className="hover:text-neutral-900">
          ← Back to course
        </Link>
      </nav>

      <Card>
        <CardHeader>
          <CardTitle>Checkout — {course.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="flex items-center justify-between rounded-md border border-neutral-200 bg-neutral-50 p-4">
            <span className="text-sm text-neutral-700">Total</span>
            <span className="text-xl font-semibold text-brand-600">
              {isFree ? "Free" : formatBDT(course.price)}
            </span>
          </div>

          {isFree ? (
            <Button
              className="w-full"
              size="lg"
              disabled={enroll.isPending}
              onClick={onFreeEnroll}
            >
              {enroll.isPending ? "Enrolling…" : "Enroll for free"}
            </Button>
          ) : (
            <form onSubmit={onPay} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="method">Payment method</Label>
                <Select id="method" {...register("method")}>
                  <option value="bkash">bKash</option>
                  <option value="nagad">Nagad</option>
                  <option value="card">Card</option>
                  <option value="manual">Manual / Bank</option>
                </Select>
              </div>

              {(method === "bkash" || method === "nagad") && (
                <div className="rounded-md bg-amber-50 p-3 text-xs text-amber-900">
                  Send <strong>{formatBDT(course.price)}</strong> to your{" "}
                  {method === "bkash" ? "bKash" : "Nagad"} merchant number, then enter
                  the transaction ID below.
                </div>
              )}

              <div className="space-y-1.5">
                <Label htmlFor="transaction_id">Transaction ID</Label>
                <Input
                  id="transaction_id"
                  placeholder="e.g. TX1234ABCD"
                  {...register("transaction_id")}
                />
                {errors.transaction_id && (
                  <p className="text-xs text-red-600">
                    {errors.transaction_id.message}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="note">Note (optional)</Label>
                <Textarea
                  id="note"
                  rows={3}
                  placeholder="Any reference info for the admin."
                  {...register("note")}
                />
              </div>

              <Button
                type="submit"
                size="lg"
                className="w-full"
                disabled={pay.isPending}
              >
                {pay.isPending ? "Submitting…" : "Submit payment"}
              </Button>
              <p className="text-center text-xs text-neutral-500">
                Your payment will be marked <strong>pending</strong> and activated by
                an admin after verification.
              </p>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
