import enum
import uuid
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                         String, Text)
from sqlalchemy.orm import relationship

from .database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class Role(str, enum.Enum):
    admin = "admin"
    editor = "editor"


class ContentStatus(str, enum.Enum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    published = "published"


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    organization = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.editor, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    content_items = relationship("Content", back_populates="owner", foreign_keys=lambda: [Content.owner_id])
    reviewed_content = relationship("Content", back_populates="reviewer", foreign_keys=lambda: [Content.reviewed_by])


class OTP(Base):
    __tablename__ = "otps"
    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    purpose = Column(String, default="signup")
    expires_at = Column(DateTime, nullable=False)
    consumed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Content(Base):
    __tablename__ = "content"
    id = Column(String, primary_key=True, default=gen_id)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, default="Poster")
    style = Column(String, default="Modern")
    aspect_ratio = Column(String, default="1:1 (Square)")
    color_theme = Column(String, default="Blue")
    prompt = Column(Text, nullable=False)
    caption = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    status = Column(Enum(ContentStatus), default=ContentStatus.draft, nullable=False)
    admin_comment = Column(Text, nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="content_items", foreign_keys=[owner_id])
    reviewer = relationship("User", back_populates="reviewed_content", foreign_keys=[reviewed_by])
    comments = relationship("Comment", back_populates="content", cascade="all, delete-orphan")
    publish_jobs = relationship("PublishJob", back_populates="content", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(String, primary_key=True, default=gen_id)
    content_id = Column(String, ForeignKey("content.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    author_role = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="comments")


class PublishJob(Base):
    __tablename__ = "publish_jobs"
    id = Column(String, primary_key=True, default=gen_id)
    content_id = Column(String, ForeignKey("content.id"), nullable=False)
    platform = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued, published, failed
    external_post_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="publish_jobs")
