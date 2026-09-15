"""Hardened file upload helpers.

Rules enforced:
1. Whitelisted extensions (image only for thumbnails).
2. Magic-byte sniffing via Pillow — never trust client-supplied content_type.
3. Size cap enforced via chunked read.
4. **Re-encoding through Pillow** — strips EXIF, defeats polyglot files
   (valid JPEG + embedded script payload), and downsizes huge originals so a
   5 MB thumbnail doesn't sit on disk forever.
5. Filenames are server-generated UUIDs; client filename never written to disk.
6. Final write path is verified to live INSIDE the configured uploads dir
   (defends against `..` and absolute-path tricks).
7. `delete_file` only deletes paths that resolve under the uploads dir.
"""

from __future__ import annotations

import io
import os
import uuid
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import settings

# Allowed image kinds and their canonical extensions.
ALLOWED_IMAGE_FORMATS: dict[str, str] = {
    "JPEG": ".jpg",
    "PNG":  ".png",
    "WEBP": ".webp",
}

THUMBNAIL_SUBDIR = "thumbnails"

# Re-encoding parameters. Thumbnails don't need to be huge; this caps disk usage
# and gives the CDN/browser a sensible upper bound to cache.
THUMBNAIL_MAX_DIM = (1600, 1600)  # max W x H, preserves aspect
THUMBNAIL_JPEG_QUALITY = 85
THUMBNAIL_WEBP_QUALITY = 85


def _uploads_root() -> Path:
    return Path(settings.UPLOAD_DIR).resolve()


def _ensure_within_uploads(path: Path) -> Path:
    """Return the resolved path if it's inside the uploads root, else raise."""
    root = _uploads_root()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid upload path") from e
    return resolved


async def _read_with_cap(file: UploadFile, max_bytes: int) -> bytes:
    """Read the upload in chunks, hard-fail past `max_bytes`."""
    chunk_size = 1024 * 64
    total = 0
    buf = io.BytesIO()
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB",
            )
        buf.write(chunk)
    return buf.getvalue()


def _sniff_image_format(raw: bytes) -> str:
    """Return PIL's format name (e.g. 'JPEG'). Raise on anything unrecognised."""
    try:
        with Image.open(io.BytesIO(raw)) as img:
            img.verify()
        with Image.open(io.BytesIO(raw)) as img2:
            fmt = img2.format
    except (UnidentifiedImageError, Exception) as e:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image") from e
    if fmt not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image format. Allowed: {', '.join(ALLOWED_IMAGE_FORMATS)}",
        )
    return fmt


def _reencode_image(raw: bytes, fmt: str) -> tuple[bytes, str, str]:
    """Decode → orient (EXIF) → resize → re-encode. Returns (bytes, format, ext).

    The production-grade step:
      - EXIF metadata (incl. GPS) is stripped because Pillow.save() doesn't carry
        it through unless you ask it to.
      - ImageOps.exif_transpose applies any EXIF orientation flag as actual pixel
        rotation BEFORE we drop the EXIF, so users still see photos right-side-up.
      - Polyglots (a file that's valid JPEG AND valid PHP) lose their non-image
        bytes because we're decoding to a pixel buffer and re-encoding from
        scratch.
      - Anything bigger than THUMBNAIL_MAX_DIM is shrunk (aspect preserved).
    """
    src = Image.open(io.BytesIO(raw))
    src.load()  # force decode now so any decode error fires here
    src = ImageOps.exif_transpose(src)

    # Resize down (in place); a no-op when the source is already small enough.
    src.thumbnail(THUMBNAIL_MAX_DIM, Image.Resampling.LANCZOS)

    out = io.BytesIO()
    if fmt == "JPEG":
        # JPEG doesn't support alpha; flatten if present.
        if src.mode in ("RGBA", "LA", "P"):
            src = src.convert("RGB")
        src.save(out, format="JPEG", quality=THUMBNAIL_JPEG_QUALITY, optimize=True, progressive=True)
        return out.getvalue(), "JPEG", ".jpg"
    if fmt == "PNG":
        src.save(out, format="PNG", optimize=True)
        return out.getvalue(), "PNG", ".png"
    # WEBP
    src.save(out, format="WEBP", quality=THUMBNAIL_WEBP_QUALITY, method=6)
    return out.getvalue(), "WEBP", ".webp"


async def save_thumbnail(file: UploadFile) -> str:
    """Save the upload, return the public URL path (e.g. /uploads/thumbnails/<uuid>.jpg)."""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Missing file")

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    raw = await _read_with_cap(file, max_bytes)

    fmt = _sniff_image_format(raw)
    encoded, _final_fmt, ext = _reencode_image(raw, fmt)

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_dir = _uploads_root() / THUMBNAIL_SUBDIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = _ensure_within_uploads(dest_dir / filename)

    with open(dest_path, "wb") as f:
        f.write(encoded)

    return f"/uploads/{THUMBNAIL_SUBDIR}/{filename}"


def delete_file(file_url: str) -> None:
    """Best-effort delete; refuses to touch anything outside the uploads dir."""
    if not file_url:
        return

    relative = file_url.split("/uploads/", 1)[-1] if "/uploads/" in file_url else file_url.lstrip("/")
    target = _uploads_root() / relative
    try:
        resolved = _ensure_within_uploads(target)
    except HTTPException:
        return  # silent: do not leak that we refused
    if resolved.exists() and resolved.is_file():
        try:
            os.remove(resolved)
        except OSError:
            pass


def allowed_image_extensions() -> Iterable[str]:
    return ALLOWED_IMAGE_FORMATS.values()
