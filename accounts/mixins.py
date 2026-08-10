from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Generic Role Mixin

    Example:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['ADMIN']
    """

    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        messages.error(
            request,
            "You are not authorized to access this page."
        )
        return redirect('unauthorized')


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']


class TeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['TEACHER']


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['STUDENT']


class AdminTeacherRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN', 'TEACHER']


class AdminStudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN', 'STUDENT']