import os
from dotenv import load_dotenv

load_dotenv()


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jzd.db")

    # Email / OTP
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "resend")
    OTP_DEBUG_EXPOSE: bool = _bool("OTP_DEBUG_EXPOSE", "false")
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM: str = os.getenv("RESEND_FROM", "JZD Content Studio <onboarding@resend.dev>")
    # Resend testing mode: all outgoing test messages are routed to this inbox.
    # Leave empty for normal recipient delivery after a sending domain is verified.
    RESEND_TEST_RECIPIENT: str = os.getenv("RESEND_TEST_RECIPIENT", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "no-reply@jzdtechnologies.com")

    # AI / Gemini
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

    # Publishing
    PUBLISH_MODE: str = os.getenv("PUBLISH_MODE", "mock")
    LINKEDIN_ACCESS_TOKEN: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    LINKEDIN_ORG_URN: str = os.getenv("LINKEDIN_ORG_URN", "")
    FACEBOOK_PAGE_ACCESS_TOKEN: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_RECIPIENT_PHONE_NUMBER: str = os.getenv("WHATSAPP_RECIPIENT_PHONE_NUMBER", "")

    SEED_ADMIN_EMAIL: str = os.getenv("SEED_ADMIN_EMAIL", "admin@jzdtechnologies.com")
    SEED_ADMIN_PASSWORD: str = os.getenv("SEED_ADMIN_PASSWORD", "Admin@12345")
    SEED_ADMIN_NAME: str = os.getenv("SEED_ADMIN_NAME", "JZD Admin")

    MEDIA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")


settings = Settings()
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
