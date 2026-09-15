"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import type { UserRole } from "@/lib/api/types";

interface NavItem {
  href: string;
  label: string;
}

const NAV: Record<UserRole, NavItem[]> = {
  admin: [
    { href: "/dashboard", label: "Overview" },
    { href: "/dashboard/admin/users", label: "Users" },
    { href: "/dashboard/admin/courses", label: "Courses" },
    { href: "/dashboard/admin/categories", label: "Categories" },
    { href: "/dashboard/admin/payments", label: "Payments" },
  ],
  teacher: [
    { href: "/dashboard", label: "Overview" },
    { href: "/dashboard/teacher/courses", label: "My courses" },
  ],
  student: [
    { href: "/dashboard/student", label: "My enrollments" },
    { href: "/dashboard/student/payments", label: "Payments" },
  ],
};

export function Sidebar({ role }: { role: UserRole }) {
  const pathname = usePathname();
  const items = NAV[role];

  return (
    <aside className="hidden w-60 shrink-0 border-r border-neutral-200 bg-white lg:block">
      <nav className="sticky top-14 flex flex-col gap-1 p-4">
        {items.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === item.href
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-brand-50 font-medium text-brand-700"
                  : "text-neutral-700 hover:bg-neutral-100"
              )}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
