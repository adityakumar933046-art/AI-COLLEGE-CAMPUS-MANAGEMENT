from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


# ==========================================================
# ADMIN REQUIRED
# ==========================================================

def admin_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "ADMIN":
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect("unauthorized")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================================
# TEACHER REQUIRED
# ==========================================================

def teacher_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "TEACHER":
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect("unauthorized")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================================
# STUDENT REQUIRED
# ==========================================================

def student_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "STUDENT":
            messages.error(
                request,
                "You are not authorized to access this page."
            )
            return redirect("unauthorized")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================================
# ADMIN OR TEACHER
# ==========================================================

def admin_or_teacher_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role not in ["ADMIN", "TEACHER"]:
            messages.error(
                request,
                "Access denied."
            )
            return redirect("unauthorized")

        return view_func(request, *args, **kwargs)

    return wrapper


# ==========================================================
# ADMIN OR STUDENT
# ==========================================================

def admin_or_student_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role not in ["ADMIN", "STUDENT"]:
            messages.error(
                request,
                "Access denied."
            )
            return redirect("unauthorized")

        return view_func(request, *args, **kwargs)

    return wrapper