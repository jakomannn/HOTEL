ADMIN_ROLE = "admin"
MANAGER_ROLE = "manager"

EMPLOYEE_ROLES = {
    ADMIN_ROLE,
    MANAGER_ROLE,
}


def normalize_role(role: str | None) -> str:
    if role is None:
        return ""

    return role.strip().lower()


def is_admin(role: str | None) -> bool:
    return normalize_role(role) == ADMIN_ROLE


def is_manager(role: str | None) -> bool:
    return normalize_role(role) in EMPLOYEE_ROLES


def is_employee(role: str | None) -> bool:
    return normalize_role(role) in EMPLOYEE_ROLES