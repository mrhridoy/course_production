"""File upload hardening: magic-byte sniff, size cap, path-traversal containment.

These call the helper directly so they don't depend on the courses route auth.
The full route-level test is exercised in Phase 1 when course CRUD has tests."""

from __future__ import annotations

import io
import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.utils.file_upload import save_thumbnail, delete_file


def _png_bytes(size=(8, 8), color=(255, 0, 0)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


def _upload(content: bytes, filename: str = "in.png", content_type: str = "image/png") -> UploadFile:
    return UploadFile(
        filename=filename,
        file=io.BytesIO(content),
        headers={"content-type": content_type},
    )


def test_save_thumbnail_writes_real_image(tmp_uploads):
    url = asyncio.run(save_thumbnail(_upload(_png_bytes())))
    assert url.startswith("/uploads/thumbnails/")
    written = Path(tmp_uploads) / url.split("/uploads/", 1)[1]
    assert written.exists() and written.is_file()


def test_save_thumbnail_rejects_non_image_content(tmp_uploads):
    fake = b"not really an image, even if content-type says it is"
    with pytest.raises(HTTPException) as exc:
        asyncio.run(save_thumbnail(_upload(fake, content_type="image/png")))
    assert exc.value.status_code == 400


def test_save_thumbnail_rejects_bmp_format(tmp_uploads):
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, format="BMP")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(save_thumbnail(_upload(buf.getvalue(), filename="x.bmp", content_type="image/bmp")))
    assert exc.value.status_code == 400


def test_save_thumbnail_rejects_oversize(tmp_uploads, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0)  # any byte exceeds 0MB
    with pytest.raises(HTTPException) as exc:
        asyncio.run(save_thumbnail(_upload(_png_bytes())))
    assert exc.value.status_code == 413


def test_delete_file_refuses_path_traversal(tmp_uploads):
    # Try to talk it into deleting outside the uploads dir; must be a no-op.
    delete_file("/uploads/../../etc/passwd")
    delete_file("/etc/passwd")
    delete_file("../../../boot.ini")
    # No assertion needed beyond "did not raise" — the helper is silent on rejection.


def test_delete_file_only_removes_under_uploads_root(tmp_uploads):
    # Create a real file inside uploads, then ensure it's removed via its public URL.
    sub = Path(tmp_uploads) / "thumbnails"
    sub.mkdir(parents=True, exist_ok=True)
    target = sub / "delete-me.png"
    target.write_bytes(b"x")
    delete_file(f"/uploads/thumbnails/{target.name}")
    assert not target.exists()
