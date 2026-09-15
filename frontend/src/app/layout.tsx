import type { Metadata, Viewport } from "next";
import { Toaster } from "sonner";
import { QueryProvider } from "@/providers/QueryProvider";
import { buildMetadata } from "@/lib/seo";
import "@/styles/globals.css";

export const metadata: Metadata = buildMetadata({
  description:
    "Learn ICT skills from expert instructors. Programming, data, design and more.",
});

export const viewport: Viewport = {
  themeColor: "#4f46e5",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryProvider>
          {children}
          <Toaster richColors position="top-right" />
        </QueryProvider>
      </body>
    </html>
  );
}
