from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Comment, Content, ContentStatus, Role, User
from ..schemas import ContentOut, DecisionIn
from ..providers.email_provider import get_email_provider
from ..security import require_role

router = APIRouter(prefix="/admin", tags=["admin"])


def _to_out(c: Content) -> ContentOut:
    out = ContentOut.model_validate(c)
    out.owner_name = c.owner.full_name if c.owner else None
    return out


@router.get("/pending", response_model=list[ContentOut])
def pending(admin: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)):
    items = (db.query(Content).filter(Content.status == ContentStatus.pending_review)
             .order_by(Content.created_at.asc()).all())
    return [_to_out(c) for c in items]


@router.get("/all", response_model=list[ContentOut])
def all_content(admin: User = Depends(require_role(Role.admin)), db: Session = Depends(get_db)):
    items = db.query(Content).order_by(Content.created_at.desc()).all()
    return [_to_out(c) for c in items]


@router.post("/{content_id}/decide", response_model=ContentOut)
def decide(content_id: str, payload: DecisionIn, admin: User = Depends(require_role(Role.admin)),
           db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.status != ContentStatus.pending_review:
        raise HTTPException(status_code=400, detail="This content isn't awaiting review.")
    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")

    content.status = ContentStatus(payload.decision)
    content.reviewed_by = admin.id
    if payload.decision == "rejected":
        content.admin_comment = payload.comment or "Changes requested."
        db.add(Comment(content_id=content.id, author_id=admin.id, author_role="admin",
                        body=content.admin_comment))
    db.commit()
    db.refresh(content)
    try:
        if content.owner:
            get_email_provider().send_decision(
                content.owner.email, content.content_type, payload.decision, content.admin_comment
            )
    except RuntimeError:
        # The review decision is already persisted; email failure should not undo it.
        pass
    return _to_out(content)
