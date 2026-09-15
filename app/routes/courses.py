import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_teacher
from app.services.course_service import CourseService
from app.schemas.course import CourseCreate, CourseUpdate, CourseOut
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[CourseOut])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CourseService(db).get_published(skip, limit)


@router.get("/all", response_model=List[CourseOut])
def list_all_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _=Depends(require_teacher)):
    return CourseService(db).get_all(skip, limit)


@router.post("/", response_model=CourseOut, status_code=201)
def create_course(data: CourseCreate, db: Session = Depends(get_db), current_user=Depends(require_teacher)):
    return CourseService(db).create(data, current_user)


# ✅ Thumbnail routes MUST come before /{course_id} routes
@router.post("/{course_id}/thumbnail")
async def upload_thumbnail(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_teacher)
):
    course = await CourseService(db).upload_thumbnail(course_id, file, current_user)
    thumbnail_url = f"{settings.BASE_URL}{course.thumbnail_url}"
    return {
        "message": "Thumbnail Uploaded Successfully",
        "course_id": course_id,
        "thumbnail_url": thumbnail_url,
    }


@router.get(
    "/{course_id}/thumbnail",
    summary="Preview Thumbnail",
)
def preview_thumbnail(
    course_id: int,
    download: bool = False,
    db: Session = Depends(get_db)
):
    """
    Returns the thumbnail image directly.
    - **Preview**: opens inline in browser / Swagger UI image viewer.
    - **Download**: add `?download=true` to get a file download prompt.
    """
    course = CourseService(db).get_by_id(course_id)

    if not course.thumbnail_url:
        raise HTTPException(status_code=404, detail="No thumbnail uploaded for this course")

    relative_path = course.thumbnail_url.replace("/uploads/", "", 1).lstrip("/")
    file_path = os.path.join(settings.UPLOAD_DIR, relative_path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Thumbnail file not found on disk")

    ext = os.path.splitext(file_path)[1].lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/png")

    filename = f"course_{course_id}_thumbnail{ext}"

    if download:
        # Forces browser to download the file
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    # Default: inline — browser/Swagger renders it as an image
    return FileResponse(
        file_path,
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename={filename}"},
    )


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return CourseService(db).get_by_id(course_id)


@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db), current_user=Depends(require_teacher)):
    return CourseService(db).update(course_id, data, current_user)


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), current_user=Depends(require_teacher)):
    CourseService(db).delete(course_id, current_user)