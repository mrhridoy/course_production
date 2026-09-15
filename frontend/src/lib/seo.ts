import type { Metadata } from "next";

const siteName = process.env.NEXT_PUBLIC_SITE_NAME ?? "ICT Bangladesh";
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export function buildMetadata(opts: {
  title?: string;
  description?: string;
  path?: string;
  image?: string;
}): Metadata {
  const title = opts.title ? `${opts.title} | ${siteName}` : siteName;
  const description =
    opts.description ?? "Online courses platform — learn ICT skills with expert instructors.";
  const url = opts.path ? `${siteUrl}${opts.path}` : siteUrl;
  const image = opts.image ?? `${siteUrl}/og-image.png`;
  return {
    title,
    description,
    metadataBase: new URL(siteUrl),
    alternates: { canonical: url },
    openGraph: {
      title,
      description,
      url,
      siteName,
      images: [{ url: image }],
      type: "website",
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
    },
  };
}

export const SITE = { name: siteName, url: siteUrl };
