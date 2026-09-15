"use client";

import Image from "next/image";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useUploadThumbnail } from "@/features/courses/mutations";
import { extractApiError } from "@/lib/api/client";
import { resolveMediaUrl } from "@/lib/format";

const MAX_BYTES = 5 * 1024 * 1024;
const ACCEPT = ["image/jpeg", "image/png", "image/webp"];

export function ThumbnailUploader({
  courseId,
  currentUrl,
}: {
  courseId: number;
  currentUrl: string | null;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  // Initialise from prop; also sync when parent refetches after successful upload.
  const [preview, setPreview] = useState<string | null>(resolveMediaUrl(currentUrl));
  const upload = useUploadThumbnail();

  // When the parent query re-fetches and passes a new currentUrl, update the
  // preview so the persisted thumbnail is shown instead of the local blob URL.
  useEffect(() => {
    if (!upload.isPending) {
      setPreview(resolveMediaUrl(currentUrl));
    }
  }, [currentUrl, upload.isPending]);

  const onPick = (file: File) => {
    if (!ACCEPT.includes(file.type)) {
      toast.error("Only JPG, PNG, or WebP allowed");
      return;
    }
    if (file.size > MAX_BYTES) {
      toast.error("Max file size is 5 MB");
      return;
    }
    const localUrl = URL.createObjectURL(file);
    setPreview(localUrl);
    upload.mutate(
      { id: courseId, file },
      {
        onSuccess: () => toast.success("Thumbnail updated"),
        onError: (err) => {
          toast.error(extractApiError(err));
          setPreview(currentUrl);
        },
      }
    );
  };

  return (
    <div className="space-y-3">
      <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-dashed border-neutral-300 bg-neutral-50">
        {preview ? (
          <Image src={resolveMediaUrl(preview) ?? preview} alt="Thumbnail" fill className="object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-neutral-500">
            No thumbnail yet
          </div>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT.join(",")}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onPick(f);
          e.target.value = "";
        }}
      />
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={upload.isPending}
        onClick={() => inputRef.current?.click()}
      >
        {upload.isPending ? "Uploading…" : currentUrl ? "Replace image" : "Upload image"}
      </Button>
      <p className="text-xs text-neutral-500">JPG / PNG / WebP, up to 5 MB.</p>
    </div>
  );
}
