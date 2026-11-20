"""Identity and authorization contracts for the future Entra middleware."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ApplicationRole(str, Enum):
    USER = "ShiftLeft.User"
    REVIEWER = "ShiftLeft.Reviewer"
    APPROVER = "ShiftLeft.Approver"
    OPERATOR = "ShiftLeft.Operator"


@dataclass(frozen=True)
class IdentityContext:
    """Trusted identity populated by authentication middleware.

    This object must come from validated Entra claims in production. Request
    payloads must never be treated as an authenticated identity.
    """

    subject_id: str
    tenant_id: str
    display_name: str | None = None
    user_principal_name: str | None = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    authentication_method: str = "entra-id"

    def has_role(self, role: ApplicationRole | str) -> bool:
        role_name = role.value if isinstance(role, ApplicationRole) else str(role)
        return role_name in self.roles

    def to_manifest(self) -> dict[str, Any]:
        return asdict(self)


def require_role(identity: IdentityContext, role: ApplicationRole) -> None:
    if not identity.has_role(role):
        raise PermissionError(f"Role required: {role.value}")


def require_any_role(identity: IdentityContext, roles: tuple[ApplicationRole, ...]) -> None:
    if not any(identity.has_role(role) for role in roles):
        raise PermissionError("One of these roles is required: " + ", ".join(role.value for role in roles))
