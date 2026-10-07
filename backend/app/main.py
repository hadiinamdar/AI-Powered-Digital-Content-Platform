from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, SessionLocal, engine
from .models import Role, User
from .routers import admin, auth, content, publish
from .security import hash_password

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JZD Content Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local development; restrict this in production
    allow_credentials=False,  # we use a Bearer token, not cookies, so this is safe with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(content.router)
app.include_router(admin.router)
app.include_router(publish.router)


@app.on_event("startup")
def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.SEED_ADMIN_EMAIL).first()
        if not existing:
            admin_user = User(
                full_name=settings.SEED_ADMIN_NAME,
                email=settings.SEED_ADMIN_EMAIL,
                organization="JZD Technologies",
                password_hash=hash_password(settings.SEED_ADMIN_PASSWORD),
                role=Role.admin,
                is_verified=True,
            )
            db.add(admin_user)
            db.commit()
            print(f"\n[SEED] Admin account ready — email: {settings.SEED_ADMIN_EMAIL} "
                  f"password: {settings.SEED_ADMIN_PASSWORD}\n")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
