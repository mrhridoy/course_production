import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-5xl font-bold">404</h1>
      <p className="text-neutral-600">We couldn&apos;t find that page.</p>
      <Link href="/">
        <Button>Back to home</Button>
      </Link>
    </div>
  );
}
