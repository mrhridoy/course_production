import Link from "next/link";
import { Button } from "@/components/ui/button";
import { buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Learn ICT skills online",
  path: "/",
});

export default function HomePage() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-20">
      <div className="mx-auto max-w-3xl text-center">
        <p className="mb-4 text-sm font-medium text-brand-600">
          ICT Bangladesh — online learning
        </p>
        <h1 className="text-4xl font-bold tracking-tight text-neutral-900 sm:text-5xl">
          Build real ICT skills with expert instructors.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-neutral-600">
          Programming, data, design and more — taught by working professionals. Learn
          at your pace, in Bangla and English.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/courses">
            <Button size="lg">Browse courses</Button>
          </Link>
          <Link href="/register">
            <Button size="lg" variant="outline">
              Sign up free
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
