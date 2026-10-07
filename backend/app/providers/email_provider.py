import json
import smtplib
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from email.mime.text import MIMEText

from ..config import settings


class EmailProvider(ABC):
    @abstractmethod
    def send_otp(self, to_email: str, code: str) -> None:
        ...

    def send_decision(self, to_email: str, content_type: str, decision: str, comment: str | None = None) -> None:
        ...


class ConsoleEmailProvider(EmailProvider):
    def send_otp(self, to_email: str, code: str) -> None:
        print(f"[EMAIL:MOCK] To: {to_email} | OTP: {code}")


class SMTPEmailProvider(EmailProvider):
    def _send(self, to_email: str, subject: str, body: str) -> None:
        if not settings.SMTP_HOST:
            raise RuntimeError("SMTP_HOST is not configured")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())

    def send_otp(self, to_email: str, code: str) -> None:
        self._send(to_email, "Your JZD Content Studio verification code",
                   f"Your verification code is: {code}\nIt expires in {settings.OTP_EXPIRE_MINUTES} minutes.")

    def send_decision(self, to_email: str, content_type: str, decision: str, comment: str | None = None) -> None:
        self._send(to_email, f"JZD Content Studio — {decision.title()}",
                   f"Your {content_type} content has been {decision}.\n\n"
                   f"Admin comment: {comment or 'No additional comment.'}")


class ResendEmailProvider(EmailProvider):
    """Real email delivery through Resend's HTTP API."""

    def _send(self, to_email: str, subject: str, html: str) -> None:
        if not settings.RESEND_API_KEY:
            raise RuntimeError("RESEND_API_KEY is not configured")
        # Resend test accounts can only deliver to the account owner's test inbox.
        # In test mode, preserve the application email as metadata in the subject and
        # route the actual message to RESEND_TEST_RECIPIENT.
        actual_recipient = to_email
        if settings.RESEND_TEST_RECIPIENT.strip() and to_email.lower() != actual_recipient.lower():
            subject = f"[Test for {to_email}] {subject}"
        payload = json.dumps({
            "from": settings.RESEND_FROM,
            "to": [actual_recipient],
            "subject": subject,
            "html": html,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "JZD-Content-Studio/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                if response.status < 200 or response.status >= 300:
                    raise RuntimeError(f"Resend returned HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Resend email failed (HTTP {exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Resend: {exc.reason}") from exc

    def send_otp(self, to_email: str, code: str) -> None:
        self._send(
            to_email,
            "Your JZD Content Studio verification code",
            f"<h2>Verify your email</h2><p>Your verification code is <strong>{code}</strong>.</p>"
            f"<p>This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.</p>",
        )

    def send_decision(self, to_email: str, content_type: str, decision: str, comment: str | None = None) -> None:
        self._send(
            to_email,
            f"JZD Content Studio — {decision.title()}",
            f"<h2>Content {decision}</h2><p>Your <strong>{content_type}</strong> has been {decision}.</p>"
            f"<p><strong>Admin comment:</strong> {comment or 'No additional comment.'}</p>",
        )


def get_email_provider() -> EmailProvider:
    if settings.EMAIL_PROVIDER == "smtp":
        return SMTPEmailProvider()
    if settings.EMAIL_PROVIDER == "console":
        return ConsoleEmailProvider()
    return ResendEmailProvider()
