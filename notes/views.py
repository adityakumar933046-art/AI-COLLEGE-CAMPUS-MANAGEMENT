def clean_query_param(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str.lower() in ("", "none", "null", "undefined"):
        return None
    return val_str

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, FileResponse, Http404

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course

from .models import Note
from .forms import NoteForm


# ==========================================
# NOTE LIST (ROLE-SECURE & FILTERABLE)
# ==========================================
@login_required
def note_list(request):
    user = request.user

    # Base Queryset with Role Security
    if user.role == "ADMIN":
        notes = Note.objects.select_related("course", "teacher", "teacher__user").all()
    elif user.role == "TEACHER":
        try:
            teacher = TeacherProfile.objects.filter(user=user).first()
            notes = Note.objects.select_related("course", "teacher", "teacher__user").filter(
                Q(teacher=teacher) | Q(course__teacher=teacher)
            )
        except TeacherProfile.DoesNotExist:
            notes = Note.objects.none()
    else:  # STUDENT
        try:
            student = StudentProfile.objects.filter(user=user).first()
            notes = Note.objects.select_related("course", "teacher", "teacher__user").filter(
                course__department=student.department, course__semester=student.semester,
                status="PUBLISHED"
            )
        except StudentProfile.DoesNotExist:
            notes = Note.objects.none()

    # Search Filter
    search = clean_query_param(request.GET.get("search"))
    if search:
        notes = notes.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(unit_topic__icontains=search) |
            Q(course__code__icontains=search) |
            Q(course__name__icontains=search) |
            Q(teacher__user__first_name__icontains=search) |
            Q(teacher__user__last_name__icontains=search)
        )

    course_id = clean_query_param(request.GET.get("course") or request.GET.get("course_id"))
    if course_id and course_id.isdigit():
        notes = notes.filter(course_id=int(course_id))

    material_type = clean_query_param(request.GET.get("material_type"))
    if material_type:
        notes = notes.filter(material_type=material_type)

    notes = notes.distinct().order_by("-uploaded_at")

    paginator = Paginator(notes, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Filter Course Options
    if user.role == "ADMIN":
        courses = Course.objects.all()
    elif user.role == "TEACHER" and hasattr(user, "teacher_profile"):
        courses = Course.objects.filter(teacher=user.teacher_profile)
    elif user.role == "STUDENT" and hasattr(user, "student_profile"):
        courses = Course.objects.filter(department=user.student_profile.department, semester=user.student_profile.semester)
    else:
        courses = Course.objects.none()

    context = {
        "notes": page_obj,
        "page_obj": page_obj,
        "search": search,
        "course_id": course_id,
        "material_type": material_type,
        "courses": courses,
    }
    return render(request, "notes/note_list.html", context)


# ==========================================
# NOTE DETAIL
# ==========================================
@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note.objects.select_related("course", "teacher", "teacher__user"), pk=pk)
    user = request.user

    # Permission check for students
    if user.role == "STUDENT":
        try:
            student = StudentProfile.objects.filter(user=user).first()
            if not Course.objects.filter(id=note.course_id, department=student.department, semester=student.semester).exists():
                messages.error(request, "You are not enrolled in the course for this study note.")
                return redirect("note_list")
        except StudentProfile.DoesNotExist:
            return redirect("note_list")

    return render(request, "notes/note_detail.html", {"note": note})


# ==========================================
# CREATE NOTE (TEACHER & ADMIN ONLY)
# ==========================================
@login_required
@admin_or_teacher_required
def note_create(request):
    user = request.user
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            note = form.save(commit=False)
            if user.role == "TEACHER":
                teacher = get_object_or_404(TeacherProfile, user=user)
                # Verify teacher owns the course
                if note.course.teacher != teacher:
                    messages.error(request, "You can only upload study notes for your assigned courses.")
                    return redirect("note_list")
                note.teacher = teacher
            elif not hasattr(note, "teacher") or not note.teacher:
                # If admin, assign course teacher or first teacher
                note.teacher = note.course.teacher or TeacherProfile.objects.first()

            note.save()
            messages.success(request, "Academic study material uploaded successfully.")
            return redirect("note_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = NoteForm(user=user)

    return render(request, "notes/note_create.html", {"form": form})


# ==========================================
# UPDATE NOTE
# ==========================================
@login_required
@admin_or_teacher_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk)
    user = request.user

    if user.role == "TEACHER" and note.teacher.user != user:
        messages.error(request, "You can only edit study notes created by you.")
        return redirect("note_list")

    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES, instance=note, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Study material updated successfully.")
            return redirect("note_detail", pk=note.pk)
    else:
        form = NoteForm(instance=note, user=user)

    return render(request, "notes/note_update.html", {"form": form, "note": note})


# ==========================================
# DELETE NOTE
# ==========================================
@login_required
@admin_or_teacher_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    user = request.user

    if user.role == "TEACHER" and note.teacher.user != user:
        messages.error(request, "You can only delete study notes created by you.")
        return redirect("note_list")

    if request.method == "POST":
        note.delete()
        messages.success(request, "Study material deleted successfully.")
        return redirect("note_list")

    return render(request, "notes/note_delete.html", {"note": note})


# ==========================================
# SECURE FILE DOWNLOAD WITH PERMISSION CHECK
# ==========================================
@login_required
def download_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    user = request.user

    # Security check for student access
    if user.role == "STUDENT":
        try:
            student = StudentProfile.objects.filter(user=user).first()
            if not Course.objects.filter(id=note.course_id, department=student.department, semester=student.semester).exists():
                messages.error(request, "Access denied: You are not enrolled in this course.")
                return redirect("note_list")
        except StudentProfile.DoesNotExist:
            return redirect("note_list")

    if not note.file or not os.path.exists(note.file.path):
        messages.warning(request, "The requested study material file is no longer available on disk.")
        return redirect("note_detail", pk=pk)

    # Increment Download Count
    note.download_count += 1
    note.save(update_fields=["download_count"])

    response = FileResponse(open(note.file.path, "rb"), as_attachment=True, filename=os.path.basename(note.file.name))
    return response


# ==========================================
# HELPER ROUTE ALIASES
# ==========================================
@login_required
def my_notes(request):
    return redirect("note_list")

@login_required
def teacher_notes(request):
    return note_list(request)
