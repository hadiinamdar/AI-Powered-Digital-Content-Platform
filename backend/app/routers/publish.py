import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Content, ContentStatus, PublishJob, User
from ..providers.publishers import get_publisher
from ..schemas import PublishIn, PublishOut, PublishResultItem
from ..security import get_current_user

router = APIRouter(prefix="/publish", tags=["publish"])


@router.post("/{content_id}", response_model=PublishOut)
def publish(content_id: str, payload: PublishIn, user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your content.")
    if content.status not in (ContentStatus.approved, ContentStatus.published):
        raise HTTPException(status_code=403, detail="Only approved content can be published.")
    if not payload.platforms:
        raise HTTPException(status_code=400, detail="Select at least one platform.")

    file_path = os.path.join(settings.MEDIA_DIR, content.file_path)
    results = []
    for platform in payload.platforms:
        publisher = get_publisher(platform)
        outcome = publisher.publish(content.caption or "", file_path)
        job = PublishJob(content_id=content.id, platform=platform,
                          status="published" if outcome.success else "failed",
                          external_post_id=outcome.external_post_id, error=outcome.error)
        db.add(job)
        results.append(PublishResultItem(platform=platform,
                                          status=job.status,
                                          external_post_id=job.external_post_id,
                                          error=job.error))
    content.status = ContentStatus.published
    db.commit()
    return PublishOut(content_id=content.id, results=results)
