from enum import Enum
from fastapi import Depends, HTTPException

from app.auth.entra import get_current_user
from app.models.resource import UserRole


class Role(str, Enum):
    ACCOUNT_ADMIN = "account_admin"
    PORTFOLIO_LEAD = "portfolio_lead"
    SUBPORTFOLIO_LEAD = "subportfolio_lead"
    TEAM_LEAD = "team_lead"
    PM = "pm"
    MEMBER = "member"


ROLE_HIERARCHY = {
    Role.ACCOUNT_ADMIN: 5,
    Role.PORTFOLIO_LEAD: 4,
    Role.SUBPORTFOLIO_LEAD: 3,
    Role.TEAM_LEAD: 2,
    Role.PM: 1,
    Role.MEMBER: 0,
}


def require_role(minimum_role: Role):
    def dependency(current_user: UserRole = Depends(get_current_user)) -> UserRole:
        try:
            user_level = ROLE_HIERARCHY[Role(current_user.role)]
        except (KeyError, ValueError):
            user_level = 0
        required_level = ROLE_HIERARCHY[minimum_role]
        if user_level < required_level:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return dependency
