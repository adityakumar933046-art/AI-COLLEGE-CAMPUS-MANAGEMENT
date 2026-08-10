from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


# ==========================================================
# CUSTOM USER MODEL
# ==========================================================

class User(AbstractUser):

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT,
        db_index=True,
    )

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    phone = models.CharField(
    max_length=15,
    blank=True,
    default="",
)
    

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True,
        default=""
    )

        # ==========================================================
    # SECURITY
    # ==========================================================

    must_change_password = models.BooleanField(
        default=False,
        help_text="Require user to change password on next login",
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Email verified or not",
    )

    is_active_account = models.BooleanField(
        default=True,
        help_text="Account active status",
    )

    password_changed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    # ==========================================================
    # SYSTEM INFORMATION
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = ["username"]

        verbose_name = "User"

        verbose_name_plural = "Users"

    def __str__(self):

        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):

        full_name = f"{self.first_name} {self.last_name}".strip()

        return full_name if full_name else self.username

    @property
    def is_admin(self):

        return self.role == self.Roles.ADMIN

    @property
    def is_teacher(self):

        return self.role == self.Roles.TEACHER

    @property
    def is_student(self):

        return self.role == self.Roles.STUDENT

    @property
    def profile_image(self):

        if self.profile_picture:

            return self.profile_picture.url

        return None
    
    # ==========================================================
# LOGIN HISTORY MODEL
# ==========================================================

class LoginHistory(models.Model):

    class LoginStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_histories",
    )

    login_status = models.CharField(
        max_length=20,
        choices=LoginStatus.choices,
        default=LoginStatus.SUCCESS,
    )

    login_time = models.DateTimeField(
        auto_now_add=True,
    )

    logout_time = models.DateTimeField(
        blank=True,
        null=True,
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    browser = models.CharField(
        max_length=255,
        blank=True,
    )

    operating_system = models.CharField(
        max_length=255,
        blank=True,
    )

    device = models.CharField(
        max_length=100,
        blank=True,
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:

        ordering = ["-login_time"]

        verbose_name = "Login History"

        verbose_name_plural = "Login Histories"

    def __str__(self):

        return (
            f"{self.user.username} | "
            f"{self.get_login_status_display()} | "
            f"{self.login_time.strftime('%d-%m-%Y %H:%M')}"
        )

    @property
    def is_logged_out(self):

        return self.logout_time is not None

    @property
    def duration(self):

        if self.logout_time:

            return self.logout_time - self.login_time

        return None
    
    # ==========================================================
# ACTIVITY LOG MODEL
# ==========================================================

class ActivityLog(models.Model):

    class Actions(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"
        PROFILE_UPDATE = "PROFILE_UPDATE", "Profile Update"
        ATTENDANCE_MARKED = "ATTENDANCE_MARKED", "Attendance Marked"
        ASSIGNMENT_CREATED = "ASSIGNMENT_CREATED", "Assignment Created"
        NOTE_UPLOADED = "NOTE_UPLOADED", "Note Uploaded"
        ANNOUNCEMENT_CREATED = "ANNOUNCEMENT_CREATED", "Announcement Created"
        LEAVE_APPLIED = "LEAVE_APPLIED", "Leave Applied"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )

    action = models.CharField(
        max_length=50,
        choices=Actions.choices,
    )

    module = models.CharField(
        max_length=50,
        blank=True,
        help_text="Students, Teachers, Attendance etc."
    )

    description = models.TextField()

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    session_key = models.CharField(
        max_length=100,
        blank=True,
    null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


# ==========================================================
# PASSWORD RESET OTP
# ==========================================================

class PasswordResetOTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )

    otp = models.CharField(
        max_length=6,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(
        default=False,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    last_resend_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - OTP"


# ==========================================================
# USER NOTIFICATIONS
# ==========================================================

class UserNotification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user.username} - {self.title}"