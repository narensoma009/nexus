import httpx
from functools import lru_cache
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.resource import UserRole


@lru_cache(maxsize=1)
def _jwks_url() -> str:
    return f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/discovery/v2.0/keys"


_jwks_cache: dict | None = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_jwks_url())
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


async def _validate_token(token: str) -> dict:
    if settings.ENVIRONMENT == "development" and not settings.ENTRA_TENANT_ID:
        # Dev shortcut: accept unsigned tokens
        try:
            return jwt.get_unverified_claims(token)
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    try:
        jwks = await _get_jwks()
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Unknown signing key")
        claims = jwt.decode(
            token,
            key,
            algorithms=[unverified.get("alg", "RS256")],
            audience=settings.ENTRA_AUDIENCE or settings.ENTRA_CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}/v2.0",
        )
        if claims.get("tid") != settings.ENTRA_TENANT_ID:
            raise HTTPException(status_code=401, detail="Invalid tenant")
        return claims
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserRole:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(" ", 1)[1]
    claims = await _validate_token(token)
    oid = claims.get("oid") or claims.get("sub")
    if not oid:
        raise HTTPException(status_code=401, detail="Token missing oid")
    res = await db.execute(select(UserRole).where(UserRole.entra_oid == oid))
    user = res.scalar_one_or_none()
    if not user:
        # Auto-provision as member with no scope
        user = UserRole(entra_oid=oid, role="member")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
