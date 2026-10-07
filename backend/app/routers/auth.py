import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import OTP, Role, User
from ..providers.email_provider import get_email_provider
from ..schemas import (LoginIn, ResendOtpIn, SignupIn, SignupOut, TokenOut,
                        VerifyOtpIn)
from ..security import create_access_token, hash_otp, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_otp(db: Session, email: str) -> str:
    code = f"{random.randint(0, 999999):06d}"
    otp = OTP(email=email, code_hash=hash_otp(code), purpose="signup",
              expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES))
    db.add(otp)
    db.commit()
    get_email_provider().send_otp(email, code)
    return code


@router.post("/signup", response_model=SignupOut)
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing and existing.is_verified:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if existing:
        existing.full_name = payload.full_name
        existing.organization = payload.organization
        existing.password_hash = hash_password(payload.password)
    else:
        existing = User(full_name=payload.full_name, email=payload.email,
                         organization=payload.organization,
                         password_hash=hash_password(payload.password),
                         role=Role.editor, is_verified=False)
        db.add(existing)
    db.commit()

    try:
        code = _issue_otp(db, payload.email)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SignupOut(message="Verification code sent.",
                      dev_otp=code if settings.OTP_DEBUG_EXPOSE else None)


@router.post("/resend-otp", response_model=SignupOut)
def resend_otp(payload: ResendOtpIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No pending signup found for this email.")
    try:
        code = _issue_otp(db, payload.email)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return SignupOut(message="A new code has been sent.",
                      dev_otp=code if settings.OTP_DEBUG_EXPOSE else None)


@router.post("/verify-otp", response_model=TokenOut)
def verify_otp(payload: VerifyOtpIn, db: Session = Depends(get_db)):
    otp = (db.query(OTP)
           .filter(OTP.email == payload.email, OTP.consumed.is_(False))
           .order_by(OTP.created_at.desc()).first())
    if not otp or otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired. Please request a new one.")
    if otp.code_hash != hash_otp(payload.code):
        raise HTTPException(status_code=400, detail="That code doesn't match.")

    otp.consumed = True
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No account found for this email.")
    user.is_verified = True
    db.commit()

    token = create_access_token(user.id, user.role.value)
    return TokenOut(access_token=token, role=user.role.value, full_name=user.full_name)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first.")
    token = create_access_token(user.id, user.role.value)
    return TokenOut(access_token=token, role=user.role.value, full_name=user.full_name)
