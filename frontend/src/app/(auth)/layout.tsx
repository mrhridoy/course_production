import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4 py-10">
      <div className="w-full max-w-md">
        <Link href="/" className="mb-6 block text-center text-base font-semibold">
          ICT<span className="text-brand-600">Bangladesh</span>
        </Link>
        {children}
      </div>
    </div>
  );
}
