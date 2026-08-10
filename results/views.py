from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Avg

from accounts.decorators import admin_or_teacher_required, admin_required
from .models import Result
from .forms import ResultForm
from students.models import StudentProfile
from teachers.models import TeacherProfile
from courses.models import Course


def calculate_sgpa(results_qs):
    total_credit_points = 0.0
    total_credits = 0
    for r in results_qs:
        credits = r.course.credits or 3
        total_credit_points += (credits * r.grade_point)
        total_credits += credits
    if total_credits > 0:
        return round(total_credit_points / total_credits, 2)
    return 0.0


@login_required
def result_list(request):
    if request.user.role == "STUDENT":
        return redirect("my_results")

    results = Result.objects.select_related("student", "student__user", "course", "teacher", "teacher__user").all()

    if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
        results = results.filter(teacher=request.user.teacher_profile)

    semester_filter = request.GET.get("semester")
    course_filter = request.GET.get("course")
    search = request.GET.get("search", "")

    if semester_filter:
        results = results.filter(semester=semester_filter)
    if course_filter:
        results = results.filter(course_id=course_filter)
    if search:
        results = results.filter(
            Q(student__user__first_name__icontains=search) |
            Q(student__user__last_name__icontains=search) |
            Q(student__roll_no__icontains=search) |
            Q(course__code__icontains=search)
        )

    courses = Course.objects.filter(status="ACTIVE")
    if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
        courses = courses.filter(teacher=request.user.teacher_profile)

    return render(
        request,
        "results/result_list.html",
        {
            "results": results,
            "courses": courses,
            "semester_filter": semester_filter,
            "course_filter": course_filter,
            "search": search,
            "title": "Academic Examination Results",
        },
    )


@login_required
def result_detail(request, pk):
    result = get_object_or_404(
        Result.objects.select_related("student", "student__user", "student__department", "course", "teacher", "teacher__user"),
        pk=pk,
    )
    return render(request, "results/result_detail.html", {"result": result, "title": f"Result - {result.student.roll_no}"})


@login_required
@admin_or_teacher_required
def result_create(request):
    if request.method == "POST":
        form = ResultForm(request.POST)
        if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
            form.fields["course"].queryset = Course.objects.filter(teacher=request.user.teacher_profile)

        if form.is_valid():
            result = form.save(commit=False)
            if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
                result.teacher = request.user.teacher_profile
            result.save()
            messages.success(request, "Result entry recorded successfully.")
            return redirect("result_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ResultForm()
        if request.user.role == "TEACHER" and hasattr(request.user, "teacher_profile"):
            form.fields["course"].queryset = Course.objects.filter(teacher=request.user.teacher_profile)
            form.fields["teacher"].initial = request.user.teacher_profile

    return render(request, "results/result_create.html", {"form": form, "title": "Enter Examination Marks"})


@login_required
@admin_or_teacher_required
def result_update(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == "POST":
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, "Result entry updated successfully.")
            return redirect("result_detail", pk=result.pk)
    else:
        form = ResultForm(instance=result)

    return render(request, "results/result_update.html", {"form": form, "result": result, "title": "Update Result Entry"})


@login_required
@admin_or_teacher_required
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == "POST":
        result.delete()
        messages.success(request, "Result entry removed successfully.")
        return redirect("result_list")
    return render(request, "results/result_delete.html", {"result": result, "title": "Delete Result Entry"})


@login_required
def my_results(request):
    try:
        student = request.user.student_profile
    except Exception:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard_redirect")

    all_results = Result.objects.filter(student=student, is_published=True).select_related("course", "teacher", "teacher__user").order_by("semester", "course__name")

    # Group by semester
    semesters_dict = {}
    for r in all_results:
        sem = r.semester
        if sem not in semesters_dict:
            semesters_dict[sem] = []
        semesters_dict[sem].append(r)

    semester_summaries = []
    for sem, res_list in sorted(semesters_dict.items()):
        sgpa = calculate_sgpa(res_list)
        tot_marks = sum(r.marks_obtained for r in res_list)
        tot_max = sum(r.total_marks for r in res_list)
        pct = round((tot_marks / tot_max * 100), 2) if tot_max > 0 else 0
        semester_summaries.append({
            "semester": sem,
            "results": res_list,
            "sgpa": sgpa,
            "total_marks": tot_marks,
            "total_max": tot_max,
            "percentage": pct,
        })

    overall_cgpa = calculate_sgpa(all_results)
    total_obtained_all = sum(r.marks_obtained for r in all_results)
    total_max_all = sum(r.total_marks for r in all_results)
    overall_pct = round((total_obtained_all / total_max_all * 100), 2) if total_max_all > 0 else 0

    return render(
        request,
        "results/my_results.html",
        {
            "student": student,
            "semester_summaries": semester_summaries,
            "cgpa": overall_cgpa,
            "overall_pct": overall_pct,
            "total_courses": all_results.count(),
            "title": "My Academic Results",
        },
    )


@login_required
def semester_results(request, semester):
    try:
        student = request.user.student_profile
    except Exception:
        return redirect("dashboard_redirect")

    results = Result.objects.filter(student=student, semester=semester, is_published=True).select_related("course", "teacher", "teacher__user")
    sgpa = calculate_sgpa(results)
    tot_marks = sum(r.marks_obtained for r in results)
    tot_max = sum(r.total_marks for r in results)
    pct = round((tot_marks / tot_max * 100), 2) if tot_max > 0 else 0

    return render(
        request,
        "results/semester_results.html",
        {
            "results": results,
            "semester": semester,
            "student": student,
            "sgpa": sgpa,
            "total_marks": tot_marks,
            "total_max": tot_max,
            "percentage": pct,
            "title": f"Semester {semester} Results",
        },
    )


@login_required
def marksheet(request, semester):
    try:
        student = request.user.student_profile
    except Exception:
        return redirect("dashboard_redirect")

    results = Result.objects.filter(student=student, semester=semester, is_published=True).select_related("course", "teacher", "teacher__user", "course__department")
    sgpa = calculate_sgpa(results)
    all_results = Result.objects.filter(student=student, is_published=True).select_related("course")
    cgpa = calculate_sgpa(all_results)

    tot_marks = sum(r.marks_obtained for r in results)
    tot_max = sum(r.total_marks for r in results)
    pct = round((tot_marks / tot_max * 100), 2) if tot_max > 0 else 0
    has_failed = any(r.grade == "F" for r in results)

    return render(
        request,
        "results/marksheet.html",
        {
            "student": student,
            "semester": semester,
            "results": results,
            "sgpa": sgpa,
            "cgpa": cgpa,
            "total_marks": tot_marks,
            "total_max": tot_max,
            "percentage": pct,
            "status_pass": not has_failed,
            "title": f"Official Marksheet - Semester {semester}",
        },
    )


@login_required
def toppers(request):
    students = StudentProfile.objects.select_related("user", "department").all()
    topper_list = []
    for s in students:
        s_results = Result.objects.filter(student=s, is_published=True).select_related("course")
        if s_results.exists():
            cgpa = calculate_sgpa(s_results)
            tot_obtained = sum(r.marks_obtained for r in s_results)
            tot_max = sum(r.total_marks for r in s_results)
            pct = round((tot_obtained / tot_max * 100), 2) if tot_max > 0 else 0
            topper_list.append({
                "student": s,
                "cgpa": cgpa,
                "percentage": pct,
                "total_courses": s_results.count(),
            })

    topper_list.sort(key=lambda x: (x["cgpa"], x["percentage"]), reverse=True)

    return render(
        request,
        "results/toppers.html",
        {
            "toppers": topper_list[:10],
            "title": "Academic Toppers & Merit List",
        },
    )
