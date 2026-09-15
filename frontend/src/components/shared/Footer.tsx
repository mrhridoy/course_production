import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-neutral-200 bg-neutral-50">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-8 text-sm text-neutral-600 sm:flex-row sm:items-center sm:justify-between">
        <p>© {new Date().getFullYear()} ICT Bangladesh. All rights reserved.</p>
        <nav className="flex gap-4">
          <Link href="/courses" className="hover:text-neutral-900">
            Courses
          </Link>
          <Link href="/login" className="hover:text-neutral-900">
            Login
          </Link>
          <Link href="/register" className="hover:text-neutral-900">
            Sign up
          </Link>
        </nav>
      </div>
    </footer>
  );
}
