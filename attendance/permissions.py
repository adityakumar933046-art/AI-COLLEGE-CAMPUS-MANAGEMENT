from django.core.exceptions import PermissionDenied


class AttendancePermission:
    """
    Centralized permission checks for Attendance Module.
    """

    @staticmethod
    def is_admin(user):
        return (
            user.is_authenticated and
            (user.is_superuser or getattr(user, "role", "") == "ADMIN")
        )

    @staticmethod
    def is_teacher(user):
        return (
            user.is_authenticated and
            getattr(user, "role", "") == "TEACHER"
        )

    @staticmethod
    def is_student(user):
        return (
            user.is_authenticated and
            getattr(user, "role", "") == "STUDENT"
        )

    @staticmethod
    def can_view_dashboard(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_mark_attendance(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_update_attendance(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_delete_attendance(user):
        return AttendancePermission.is_admin(user)

    @staticmethod
    def can_create_session(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_close_session(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_view_reports(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_export_reports(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_view_defaulters(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_view_analytics(user):
        return (
            AttendancePermission.is_admin(user) or
            AttendancePermission.is_teacher(user)
        )

    @staticmethod
    def can_view_student_attendance(user, student_user=None):
        """
        Admin/Teacher can view everyone.
        Student can view only their own attendance.
        """

        if AttendancePermission.is_admin(user):
            return True

        if AttendancePermission.is_teacher(user):
            return True

        if (
            AttendancePermission.is_student(user)
            and student_user is not None
            and user.pk == student_user.pk
        ):
            return True

        return False


# ==========================================================
# Helper Functions (Raise PermissionDenied Automatically)
# ==========================================================

def require_admin(user):
    if not AttendancePermission.is_admin(user):
        raise PermissionDenied("Administrator permission required.")


def require_teacher(user):
    if not AttendancePermission.is_teacher(user):
        raise PermissionDenied("Teacher permission required.")


def require_admin_or_teacher(user):
    if not (
        AttendancePermission.is_admin(user) or
        AttendancePermission.is_teacher(user)
    ):
        raise PermissionDenied(
            "Admin or Teacher permission required."
        )


def require_student(user):
    if not AttendancePermission.is_student(user):
        raise PermissionDenied("Student permission required.")