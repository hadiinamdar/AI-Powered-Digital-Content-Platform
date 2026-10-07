import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Comment, Content, ContentStatus, User
from ..providers.ai_provider import get_ai_provider
from ..schemas import CommentIn, CommentOut, ContentOut, GenerateIn
from ..security import get_current_user

router = APIRouter(prefix="/content", tags=["content"])


def _to_out(c: Content) -> ContentOut:
    out = ContentOut.model_validate(c)
    out.owner_name = c.owner.full_name if c.owner else None
    return out


@router.post("/generate", response_model=ContentOut)
def generate(payload: GenerateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        asset = get_ai_provider().generate(payload.prompt, payload.content_type,
                                            payload.style, payload.color_theme)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    content = Content(owner_id=user.id, content_type=payload.content_type, style=payload.style,
                       aspect_ratio=payload.aspect_ratio, color_theme=payload.color_theme,
                       prompt=payload.prompt, caption=asset.caption, status=ContentStatus.draft)
    db.add(content)
    db.flush()  # get content.id before writing the file

    file_name = f"{content.id}.{asset.file_ext}"
    file_path = os.path.join(settings.MEDIA_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(asset.file_bytes)
    content.file_path = file_name
    db.commit()
    db.refresh(content)
    return _to_out(content)


@router.post("/{content_id}/submit", response_model=ContentOut)
def submit_for_review(content_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You can only submit your own content.")
    content.status = ContentStatus.pending_review
    content.admin_comment = None
    db.commit()
    db.refresh(content)
    return _to_out(content)


@router.get("/mine", response_model=list[ContentOut])
def my_content(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = (db.query(Content).filter(Content.owner_id == user.id)
             .order_by(Content.created_at.desc()).all())
    return [_to_out(c) for c in items]


@router.get("/{content_id}", response_model=ContentOut)
def get_content(content_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not your content.")
    return _to_out(content)


@router.get("/{content_id}/download")
def download(content_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not your content.")
    # This is the real, server-enforced gate: even if someone calls the API
    # directly, the file will not be served until an admin has approved it.
    if content.status != ContentStatus.approved and content.status != ContentStatus.published:
        raise HTTPException(status_code=403, detail="This content hasn't been approved for download yet.")
    path = os.path.join(settings.MEDIA_DIR, content.file_path)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on server.")
    return FileResponse(path, filename=f"jzd-{content.content_type.lower()}-{content.id[:8]}.svg")


@router.post("/{content_id}/comments", response_model=CommentOut)
def add_comment(content_id: str, payload: CommentIn, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not your content.")
    comment = Comment(content_id=content_id, author_id=user.id, author_role=user.role.value, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{content_id}/comments", response_model=list[CommentOut])
def list_comments(content_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id and user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not your content.")
    return (db.query(Comment).filter(Comment.content_id == content_id)
            .order_by(Comment.created_at.asc()).all())
