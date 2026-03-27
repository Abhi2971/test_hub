"""
RBAC (Role-Based Access Control) for ExamSaaS platform.
Permission matrix and helper functions.
"""
import logging
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


PERMISSIONS = {
    "super_admin": ["*"],
    
    "admin_public": [
        "exam:create",
        "exam:publish",
        "exam:read",
        "question:create",
        "question:read",
        "question:approve",
        "pdf:upload",
        "pdf:read",
        "ebook:create",
        "ebook:read",
        "analytics:platform",
        "ai:generate_questions",
    ],
    
    "admin_college": [
        "exam:read",
        "exam:approve",
        "exam:reject",
        "user:create_teacher",
        "user:read",
        "user:deactivate",
        "student:read",
        "student:bulk_upload",
        "analytics:institute",
        "result:export",
        "subscription:manage",
        "ebook:read",
    ],
    
    "teacher": [
        "exam:create",
        "exam:read",
        "exam:update",
        "exam:delete",
        "exam:publish",
        "exam:generate_magic_link",
        "exam:monitor_live",
        "question:create",
        "question:read",
        "question:update",
        "student:create",
        "student:read",
        "student:update",
        "student:bulk_upload",
        "student:reset_credentials",
        "attempt:force_submit",
        "result:read",
        "result:export",
        "ai:generate_questions",
    ],
    
    "student_registered": [
        "exam:read_public",
        "exam:purchase",
        "attempt:create",
        "attempt:read_own",
        "result:read_own",
        "wallet:read",
        "wallet:topup",
        "certificate:read_own",
        "ebook:read",
        "ai:recommendations",
    ],
    
    "student_assigned": [
        "exam:read_assigned",
        "attempt:create",
        "attempt:read_own",
        "result:read_own",
    ],
    
    "support_agent": [
        "user:read_masked",
        "exam:read",
        "result:read",
        "ticket:create",
        "ticket:read",
        "ticket:update",
        "ticket:assign",
        "ticket:escalate",
        "ticket:close",
        "user:reset_password",
        "attempt:resend_magic_link",
    ],
}


AUDIT_LOGGED_ACTIONS = {
    "impersonate_admin",
    "force_submit_attempt",
    "revoke_certificate",
    "delete_student",
    "reset_student_credentials",
    "suspend_institute",
    "restore_institute",
    "admin_credit_wallet",
}


def has_permission(role: str, action: str) -> bool:
    """
    Check if a role has permission to perform an action.
    
    Args:
        role: User role
        action: Permission action (e.g., "exam:create")
    
    Returns:
        True if role has permission, False otherwise
    """
    if role not in PERMISSIONS:
        logger.warning(f"Unknown role: {role}")
        return False
    
    permissions = PERMISSIONS[role]
    
    if "*" in permissions:
        return True
    
    return action in permissions


def has_any_permission(role: str, actions: List[str]) -> bool:
    """
    Check if a role has any of the specified permissions.
    
    Args:
        role: User role
        actions: List of permission actions
    
    Returns:
        True if role has any permission, False otherwise
    """
    return any(has_permission(role, action) for action in actions)


def has_all_permissions(role: str, actions: List[str]) -> bool:
    """
    Check if a role has all of the specified permissions.
    
    Args:
        role: User role
        actions: List of permission actions
    
    Returns:
        True if role has all permissions, False otherwise
    """
    return all(has_permission(role, action) for action in actions)


def get_permissions(role: str) -> Set[str]:
    """
    Get all permissions for a role.
    
    Args:
        role: User role
    
    Returns:
        Set of permission strings
    """
    if role not in PERMISSIONS:
        return set()
    
    return set(PERMISSIONS[role])


def check_institute_scope(user: 'User', target_institute_id: str) -> bool:
    """
    Check if user has access to target institute.
    
    Args:
        user: User object
        target_institute_id: Institute ID to check
    
    Returns:
        True if user has access, False otherwise
    """
    if user.role == "super_admin":
        return True
    
    if user.institute and str(user.institute.id) == str(target_institute_id):
        return True
    
    return False


def check_institute_scope_by_id(user_id: str, user_role: str, user_institute_id: Optional[str], 
                                target_institute_id: str) -> bool:
    """
    Check if user has access to target institute (using IDs).
    
    Args:
        user_id: User ID
        user_role: User role
        user_institute_id: User's institute ID
        target_institute_id: Target institute ID
    
    Returns:
        True if user has access, False otherwise
    """
    if user_role == "super_admin":
        return True
    
    if user_institute_id and str(user_institute_id) == str(target_institute_id):
        return True
    
    return False


def is_super_admin(role: str) -> bool:
    """Check if role is super_admin."""
    return role == "super_admin"


def is_platform_admin(role: str) -> bool:
    """Check if role is platform admin (super_admin or admin_public)."""
    return role in ["super_admin", "admin_public"]


def is_institute_admin(role: str) -> bool:
    """Check if role is institute admin."""
    return role in ["super_admin", "admin_public", "admin_college"]


def is_teacher(role: str) -> bool:
    """Check if role is teacher."""
    return role == "teacher"


def is_student(role: str) -> bool:
    """Check if role is student."""
    return role in ["student_registered", "student_assigned"]


def requires_institute(role: str) -> bool:
    """Check if role requires an institute context."""
    return role in ["admin_college", "teacher", "student_assigned"]


def get_role_display_name(role: str) -> str:
    """Get human-readable role name."""
    names = {
        "super_admin": "Super Admin",
        "admin_public": "Platform Admin",
        "admin_college": "Institute Admin",
        "teacher": "Teacher",
        "student_registered": "Registered Student",
        "student_assigned": "Assigned Student",
        "support_agent": "Support Agent",
    }
    return names.get(role, role)


def requires_audit_log(action: str) -> bool:
    """
    Check if an action requires audit logging.
    
    Args:
        action: Action name
    
    Returns:
        True if action requires audit log, False otherwise
    """
    return action in AUDIT_LOGGED_ACTIONS
