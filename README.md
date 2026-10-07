# JZD Content Studio — full-stack app

A real, working implementation of the sign-up → OTP → AI-generate → admin-review →
publish flow: FastAPI backend with a real database, real password hashing,
real JWT sessions, and real server-enforced permissions (the download is
blocked at the API level until an admin approves — not just hidden in the UI).

It runs immediately with **zero API keys**, using mock providers for
email/AI/publishing. Each one is a swappable interface — flip one setting in
`.env` and add your real credentials to go live, without touching the rest
of the code.

## What's real vs. mocked, honestly

| Piece | Right now (default) | To make it live |
|---|---|---|
| Accounts, passwords, sessions | 100% real (bcrypt + JWT + SQLite) | Nothing to change |
| Roles & permissions | 100% real, enforced server-side | Nothing to change |
| OTP delivery | Printed to the backend terminal + returned in the API response | Set `EMAIL_PROVIDER=smtp` + SMTP credentials in `.env` |
| AI content generation | A real, working placeholder generator (no API key needed) | Set `AI_PROVIDER=claude` + `ANTHROPIC_API_KEY` in `.env` |
| Social publishing | Simulated success, but the real queue/status pipeline runs | Set `PUBLISH_MODE=live` + platform credentials (needs approved developer apps) |

## 1. Run the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # defaults work as-is
uvicorn app.main:app --reload --port 8000
```

On first run it creates `jzd.db` (SQLite) and prints a seeded admin login to
the terminal:

```
[SEED] Admin account ready — email: admin@jzdtechnologies.com password: Admin@12345
```

Open http://localhost:8000/docs to see the live, interactive API
documentation (Swagger UI) — every endpoint below is real and callable there.

## 2. Open the frontend

Just open `frontend/index.html` directly in a browser. It talks to the
backend at `http://localhost:8000` (edit the `API_BASE` constant at the top
of the `<script>` in `index.html` if your backend runs elsewhere).

## 3. Try the full flow

1. **Create New Account** → fill in the form → **Send OTP**
2. Since `EMAIL_PROVIDER=console` by default, the code appears in a toast
   *and* in the backend terminal — enter it and verify
3. Sign in → **Generate with AI** → write a prompt → **Generate Content**
4. **Submit to Admin**
5. Click **"Preview: open the admin's review link"** — this signs into the
   seeded admin account in the same tab, purely so you can demo both sides
   of the flow without opening a second browser. In a real deployment the
   admin reviews from their own account in their own session.
6. **Accept** → back on the user's side, **Download content** now works
   (try it *before* approval and the API correctly returns `403`)
7. **Proceed to Publish** → pick platforms → **Publish Now**

## Project structure

```
backend/app/
  main.py            FastAPI app, CORS, startup admin seeding
  models.py          User, OTP, Content, Comment, PublishJob (SQLAlchemy)
  schemas.py         Request/response models (Pydantic)
  security.py        Password hashing, JWT, role-based access dependencies
  providers/
    email_provider.py   EmailProvider interface — Console (default) / SMTP
    ai_provider.py       AIProvider interface — Mock (default) / Claude
    publishers.py        BasePublisher interface — Mock (default) / LinkedIn / Facebook / Instagram / WhatsApp
  routers/
    auth.py, content.py, admin.py, publish.py
frontend/
  index.html         The full UI, calling the API with fetch()
```

## Adding a new social platform later

This is the exact Adapter/Factory pattern from the architecture doc, made
real: open `backend/app/providers/publishers.py`, add a class implementing
`BasePublisher.publish()`, and register it in the `_LIVE_PUBLISHERS` dict.
Nothing else in the system needs to change.

## Notes on going live

- **Email**: any SMTP provider works (SendGrid, Mailgun, your own mail
  server) — just fill in the `SMTP_*` values in `.env`.
- **AI**: `ClaudeAIProvider` in `ai_provider.py` shows exactly where to call
  a real model; it currently writes the AI's headline into the same
  placeholder graphic. Swap in an image-generation model there if you want
  real poster artwork instead of the placeholder layout.
- **Social publishing**: LinkedIn, Facebook, Instagram and WhatsApp each require an
  approved developer/Business Platform app and OAuth credentials before their real API calls
  will work — this is normal and outside what any code alone can do. The
  adapters are written and ready; they return a clear "not implemented yet"
  error until you add real access tokens, rather than silently failing.
- **Deployment**: containerize with Docker and put a real Postgres database
  behind `DATABASE_URL` when you're ready to move off SQLite — the code
  doesn't need to change, since it's a plain SQLAlchemy URL.


## WhatsApp support

WhatsApp is available in the **Publish to Social Media** screen and is enabled
by default alongside Facebook, Instagram, and LinkedIn. In the default
`PUBLISH_MODE=mock`, selecting WhatsApp runs through the same end-to-end
publish/status pipeline as the other platforms.

For a live WhatsApp Business Cloud API integration, configure:

```env
PUBLISH_MODE=live
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_RECIPIENT_PHONE_NUMBER=
```

The adapter intentionally does not claim a live publish from a local file.
A production implementation must upload media through the WhatsApp Business
Cloud API (or expose the media through a public URL), send the appropriate
message/media payload, and handle delivery/status webhooks.
