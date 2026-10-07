import random
import string
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..config import settings


@dataclass
class PublishResult:
    success: bool
    external_post_id: Optional[str] = None
    error: Optional[str] = None


class BasePublisher(ABC):
    """The contract every platform adapter implements. To add a new
    platform: write one class implementing publish(), then register it
    in PUBLISHERS below. Nothing else in the system needs to change."""

    @abstractmethod
    def publish(self, caption: str, file_path: str) -> PublishResult:
        ...


def _fake_id() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


class MockPublisher(BasePublisher):
    """Simulates a successful publish with no credentials needed, so the
    whole pipeline (queue → publish → status) is genuinely exercised end
    to end. Used automatically while PUBLISH_MODE=mock."""

    def __init__(self, platform: str):
        self.platform = platform

    def publish(self, caption: str, file_path: str) -> PublishResult:
        time.sleep(0.3)  # simulate network latency
        return PublishResult(success=True, external_post_id=f"{self.platform.lower()}_{_fake_id()}")


class LinkedInPublisher(BasePublisher):
    def publish(self, caption: str, file_path: str) -> PublishResult:
        if not settings.LINKEDIN_ACCESS_TOKEN:
            return PublishResult(success=False, error="LINKEDIN_ACCESS_TOKEN is not set in .env")
        # Real integration point: POST to
        # https://api.linkedin.com/v2/ugcPosts using settings.LINKEDIN_ACCESS_TOKEN
        # and settings.LINKEDIN_ORG_URN. Left unimplemented here since it
        # requires an approved LinkedIn developer app.
        return PublishResult(success=False, error="Live LinkedIn publishing not implemented yet — "
                                                    "see providers/publishers.py")


class FacebookPublisher(BasePublisher):
    def publish(self, caption: str, file_path: str) -> PublishResult:
        if not settings.FACEBOOK_PAGE_ACCESS_TOKEN:
            return PublishResult(success=False, error="FACEBOOK_PAGE_ACCESS_TOKEN is not set in .env")
        # Real integration point: POST to
        # https://graph.facebook.com/{settings.FACEBOOK_PAGE_ID}/photos
        return PublishResult(success=False, error="Live Facebook publishing not implemented yet — "
                                                    "see providers/publishers.py")


class InstagramPublisher(BasePublisher):
    def publish(self, caption: str, file_path: str) -> PublishResult:
        if not settings.INSTAGRAM_ACCESS_TOKEN:
            return PublishResult(success=False, error="INSTAGRAM_ACCESS_TOKEN is not set in .env")
        # Real integration point: create a media container, then publish it,
        # per Instagram's Graph API content-publishing flow. The account
        # must be a Business or Creator account and the media must be
        # reachable at a public URL when the API attempts to fetch it.
        return PublishResult(success=False, error="Live Instagram publishing not implemented yet — "
                                                    "see providers/publishers.py")


class WhatsAppPublisher(BasePublisher):
    """WhatsApp Business Cloud API adapter.

    The live integration requires a WhatsApp Business Cloud API access token,
    phone number ID, and a publicly reachable media URL. This project keeps
    the adapter explicit rather than pretending that a local filesystem path
    can be uploaded directly to WhatsApp.
    """
    def publish(self, caption: str, file_path: str) -> PublishResult:
        if not settings.WHATSAPP_ACCESS_TOKEN:
            return PublishResult(success=False, error="WHATSAPP_ACCESS_TOKEN is not set in .env")
        if not settings.WHATSAPP_PHONE_NUMBER_ID:
            return PublishResult(success=False, error="WHATSAPP_PHONE_NUMBER_ID is not set in .env")
        if not settings.WHATSAPP_RECIPIENT_PHONE_NUMBER:
            return PublishResult(success=False, error="WHATSAPP_RECIPIENT_PHONE_NUMBER is not set in .env")
        # Real integration point: WhatsApp Business Cloud API /messages.
        # For image/status publishing, upload the media first and then send
        # the resulting media ID or use a public media URL. A production
        # deployment should also add WhatsApp webhook/status handling.
        return PublishResult(success=False, error="Live WhatsApp publishing not implemented yet — see providers/publishers.py")


_LIVE_PUBLISHERS = {
    "LinkedIn": LinkedInPublisher,
    "Facebook": FacebookPublisher,
    "Instagram": InstagramPublisher,
    "WhatsApp": WhatsAppPublisher,
}


def get_publisher(platform: str) -> BasePublisher:
    if settings.PUBLISH_MODE == "live" and platform in _LIVE_PUBLISHERS:
        return _LIVE_PUBLISHERS[platform]()
    return MockPublisher(platform)
