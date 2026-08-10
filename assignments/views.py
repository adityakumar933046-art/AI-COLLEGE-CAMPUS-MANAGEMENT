import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from accounts.decorators import admin_required, admin_or_teacher_required
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course

from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, AssignmentSubmissionForm, AssignmentMarksForm


# ==========================================
# ASSIGNMENT LIST
# ==========================================
@login_required
def assignment_list(request):
    user = request.user
    today = timezone.now().date()

    if user.role == "ADMIN":
        assignments = Assignment.objects.select_related("course", "teacher", "teacher__user").all()
    elif user.role == "TEACHER":
        try:
            teacher = TeacherProfile.objects.get(user=user)
            assignments = Assignment.objects.select_related("course", "teacher", "teacher__user").filter(teacher=teacher)
        except TeacherProfile.DoesNotExist:
            assignments = Assignment.objects.none()
    else:  # STUDENT
        try:
            student = StudentProfile.objects.get(user=user)
            assignments = Assignment.objects.select_related("course", "teacher", "teacher__user").filter(
                course__department=student.department, course__semester=student.semester
            )
        except StudentProfile.DoesNotExist:
            assignments = Assignment.objects.none()

    search = request.GET.get("search")
    if search:
        assignments = assignments.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(course__code__icontains=search) |
            Q(course__name__icontains=search) |
            Q(teacher__user__first_name__icontains=search) |
            Q(teacher__user__last_name__icontains=search)
        )

    course_id = request.GET.get("course")
    if course_id:
        assignments = assignments.filter(course_id=course_id)

    assignments = assignments.distinct().order_by("due_date", "-created_at")

    # Get student submissions dict
    submitted_dict = {}
    if user.role == "STUDENT" and hasattr(user, "student_profile"):
        subs = AssignmentSubmission.objects.filter(student=user.student_profile)
        for s in subs:
            submitted_dict[s.assignment_id] = s

    paginator = Paginator(assignments, 10)
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
        "assignments": page_obj,
        "page_obj": page_obj,
        "search": search,
        "course_id": course_id,
        "courses": courses,
        "today": today,
        "submitted_dict": submitted_dict,
    }
    return render(request, "assignments/assignment_list.html", context)


# ==========================================
# ASSIGNMENT DETAIL
# ==========================================
@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related("course", "teacher", "teacher__user"), pk=pk)
    user = request.user
    today = timezone.now().date()
    submission = None

    if user.role == "STUDENT" and hasattr(user, "student_profile"):
        submission = AssignmentSubmission.objects.filter(assignment=assignment, student=user.student_profile).first()

    context = {
        "assignment": assignment,
        "submission": submission,
        "today": today,
    }
    return render(request, "assignments/assignment_detail.html", context)


# ==========================================
# CREATE ASSIGNMENT
# ==========================================
@login_required
@admin_or_teacher_required
def assignment_create(request):
    user = request.user
    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            assignment = form.save(commit=False)
            if user.role == "TEACHER":
                teacher = get_object_or_404(TeacherProfile, user=user)
                if assignment.course.teacher != teacher:
                    messages.error(request, "You can only create assignments for your assigned courses.")
                    return redirect("assignment_list")
                assignment.teacher = teacher
            elif not hasattr(assignment, "teacher") or not assignment.teacher:
                assignment.teacher = assignment.course.teacher or TeacherProfile.objects.first()

            assignment.save()
            messages.success(request, "Assignment created successfully.")
            return redirect("assignment_list")
    else:
        form = AssignmentForm(user=user)

    return render(request, "assignments/assignment_create.html", {"form": form})


# ==========================================
# UPDATE ASSIGNMENT
# ==========================================
@login_required
@admin_or_teacher_required
def assignment_update(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user

    if user.role == "TEACHER" and assignment.teacher.user != user:
        messages.error(request, "You can only edit assignments created by you.")
        return redirect("assignment_list")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully.")
            return redirect("assignment_detail", pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment, user=user)

    return render(request, "assignments/assignment_update.html", {"form": form, "assignment": assignment})


# ==========================================
# DELETE ASSIGNMENT
# ==========================================
@login_required
@admin_or_teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user

    if user.role == "TEACHER" and assignment.teacher.user != user:
        messages.error(request, "You can only delete assignments created by you.")
        return redirect("assignment_list")

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        return redirect("assignment_list")

    return render(request, "assignments/assignment_delete.html", {"assignment": assignment})


# ==========================================
# SUBMIT ASSIGNMENT (STUDENT ONLY)
# ==========================================
@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user

    if user.role != "STUDENT":
        messages.error(request, "Only students can submit assignments.")
        return redirect("assignment_detail", pk=pk)

    student = get_object_or_404(StudentProfile, user=user)

    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub, created = AssignmentSubmission.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={"file": form.cleaned_data["file"]}
            )
            if not created:
                sub.file = form.cleaned_data["file"]
                sub.submitted_at = timezone.now()
                sub.save()

            messages.success(request, "Assignment solution submitted successfully.")
            return redirect("assignment_detail", pk=pk)
    else:
        form = AssignmentSubmissionForm()

    return render(request, "assignments/submit_assignment.html", {"form": form, "assignment": assignment})


# ==========================================
# SUBMISSION LIST (TEACHER & ADMIN)
# ==========================================
@login_required
@admin_or_teacher_required
def submission_list(request):
    user = request.user
    assignment_id = request.GET.get("assignment_id")

    if user.role == "ADMIN":
        submissions = AssignmentSubmission.objects.select_related("assignment", "assignment__course", "student", "student__user").all()
    else:
        teacher = get_object_or_404(TeacherProfile, user=user)
        submissions = AssignmentSubmission.objects.select_related("assignment", "assignment__course", "student", "student__user").filter(
            assignment__teacher=teacher
        )

    if assignment_id:
        submissions = submissions.filter(assignment_id=assignment_id)

    submissions = submissions.order_by("-submitted_at")

    paginator = Paginator(submissions, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "submissions": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "assignments/submission_list.html", context)


# ==========================================
# UPDATE MARKS & FEEDBACK (TEACHER & ADMIN)
# ==========================================
@login_required
@admin_or_teacher_required
def update_marks(request, pk):
    submission = get_object_or_404(AssignmentSubmission.objects.select_related("assignment", "student", "student__user"), pk=pk)
    user = request.user

    if user.role == "TEACHER" and submission.assignment.teacher.user != user:
        messages.error(request, "You can only grade submissions for your assigned courses.")
        return redirect("submission_list")

    if request.method == "POST":
        form = AssignmentMarksForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.status = "GRADED"
            sub.save()
            messages.success(request, "Submission graded successfully.")
            return redirect("submission_list")
    else:
        form = AssignmentMarksForm(instance=submission)

    return render(request, "assignments/update_marks.html", {"form": form, "submission": submission})
