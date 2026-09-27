import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.security import create_access_token, hash_password, verify_password
from src.db.session import get_db
from src.models.user import User
from src.schemas.auth import TokenResponse, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="このメールアドレスは既に登録されています"
        )

    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/guest", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def guest_login(db: Session = Depends(get_db)) -> TokenResponse:
    """デモ・動作確認用。使い捨てのゲストアカウントを作成してその場でログインする。"""
    guest_email = f"guest-{uuid.uuid4().hex[:12]}@example.com"
    user = User(email=guest_email, hashed_password=hash_password(uuid.uuid4().hex))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="メールアドレスまたはパスワードが違います"
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)
