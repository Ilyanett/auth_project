from .models import UserRole, AccessRule


def get_user_role(user):
    user_role = UserRole.objects.filter(user=user).first()
    if not user_role:
        return None
    return user_role.role


def has_permission(user, element_name: str, permission: str) -> bool:
    role = get_user_role(user)
    if not role:
        return False

    try:
        rule = AccessRule.objects.get(
            role=role,
            element__name=element_name
        )
        return getattr(rule, permission, False)
    except AccessRule.DoesNotExist:
        return False
