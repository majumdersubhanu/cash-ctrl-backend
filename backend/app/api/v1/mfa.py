import pyotp
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User

router = APIRouter(tags=["security"])


class MFAVerifyPayload(BaseModel):
    token: str


@router.post("/setup")
async def setup_mfa(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if user.is_mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled."
        )

    # Generate a new 16-character base32 secret
    secret = pyotp.random_base32()
    user.totp_secret = secret
    db.add(user)
    await db.commit()

    # Generate provisioning URI for authenticator apps (Google Authenticator, Authy, etc)
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email, issuer_name="CashCtrl"
    )

    return {"secret": secret, "qr_code_uri": uri}


@router.post("/verify")
async def verify_mfa(
    payload: MFAVerifyPayload,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup has not been initiated.",
        )

    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(payload.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP token."
        )

    # Token is valid, enable MFA globally for the user if it wasn't already.
    if not user.is_mfa_enabled:
        user.is_mfa_enabled = True
        db.add(user)
        await db.commit()

    return {"status": "ok", "message": "MFA verified successfully."}
