"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useMyEnrollments, useEnroll } from "@/features/enrollments/hooks";
import { extractApiError } from "@/lib/api/client";

interface Props {
  courseId: number;
  price: number;
}

/**
 * Smart enroll CTA shown on the public course detail page.
 *
 * States:
 *  - Loading  → disabled skeleton so user can't click before we know status
 *  - Enrolled → "Go to my courses" link (no re-enroll possible)
 *  - Free     → "Enroll for free" — calls API directly, shows toast on error
 *  - Paid     → "Buy & enroll" — navigates to checkout
 */
export function CourseEnrollButton({ courseId, price }: Props) {
  const router = useRouter();
  const { data: enrollments, isLoading } = useMyEnrollments();
  const enroll = useEnroll();

  // While we're checking enrollment status show a neutral disabled button
  if (isLoading) {
    return (
      <Button className="w-full" size="lg" disabled>
        Loading…
      </Button>
    );
  }

  const isEnrolled = enrollments?.some((e) => e.course_id === courseId) ?? false;

  if (isEnrolled) {
    return (
      <Link href="/dashboard/student">
        <Button className="w-full" size="lg" variant="outline">
          ✓ Already enrolled — Go to my courses
        </Button>
      </Link>
    );
  }

  // Paid course → go to checkout
  if (price > 0) {
    return (
      <Link href={`/dashboard/student/checkout/${courseId}`}>
        <Button className="w-full" size="lg">
          Buy &amp; enroll
        </Button>
      </Link>
    );
  }

  // Free course → enroll directly, show toast on any backend error
  const handleFreeEnroll = () => {
    enroll.mutate(courseId, {
      onSuccess: () => {
        toast.success("Enrolled successfully!");
        router.push("/dashboard/student");
      },
      onError: (err) => {
        toast.error(extractApiError(err));
      },
    });
  };

  return (
    <Button
      className="w-full"
      size="lg"
      disabled={enroll.isPending}
      onClick={handleFreeEnroll}
    >
      {enroll.isPending ? "Enrolling…" : "Enroll for free"}
    </Button>
  );
}
