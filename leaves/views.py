from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.decorators import admin_required

from .models import Leave
from .forms import LeaveForm


# ==========================================
# LEAVE LIST (ADMIN)
# ==========================================

@login_required
@admin_required
def leave_list(request):

    leaves = Leave.objects.select_related(
        "applicant"
    ).all()

    search = request.GET.get("search")

    if search:

        leaves = leaves.filter(

            Q(applicant__username__icontains=search) |
            Q(applicant__first_name__icontains=search) |
            Q(applicant__last_name__icontains=search) |
            Q(reason__icontains=search)

        )

    paginator = Paginator(leaves, 10)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "leaves/leave_list.html",
        {
            "leaves": page_obj,
            "page_obj": page_obj,
            "search": search,
        }
    )


# ==========================================
# MY LEAVES
# ==========================================

@login_required
def my_leaves(request):

    leaves = Leave.objects.filter(
        applicant=request.user
    ).order_by("-applied_at")

    return render(
        request,
        "leaves/my_leaves.html",
        {
            "leaves": leaves
        }
    )


# ==========================================
# APPLY LEAVE
# ==========================================

@login_required
def apply_leave(request):

    if request.method == "POST":

        form = LeaveApplicationForm(
    request.POST,
    request.FILES
)

        if form.is_valid():

            leave = form.save(commit=False)

            leave.applicant = request.user

            leave.save()

            messages.success(
                request,
                "Leave applied successfully."
            )

            return redirect(
                "my_leaves"
            )

    else:

        form = LeaveForm()

    return render(
        request,
        "leaves/apply_leave.html",
        {
            "form": form
        }
    )
from .forms import LeaveStatusForm


# ==========================================
# LEAVE DETAIL
# ==========================================

@login_required
def leave_detail(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if not request.user.is_staff and leave.applicant != request.user:

        messages.error(
            request,
            "You are not authorized to view this leave."
        )

        return redirect("my_leaves")

    return render(
        request,
        "leaves/leave_detail.html",
        {
            "leave": leave
        }
    )


# ==========================================
# UPDATE LEAVE STATUS (ADMIN)
# ==========================================

@login_required
@admin_required
def update_leave_status(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if request.method == "POST":

        form = LeaveStatusForm(
            request.POST,
            instance=leave
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Leave status updated successfully."
            )

            return redirect(
                "leave_list"
            )

    else:

        form = LeaveStatusForm(
            instance=leave
        )

    return render(
        request,
        "leaves/update_leave_status.html",
        {
            "form": form,
            "leave": leave
        }
    )


# ==========================================
# DELETE LEAVE
# ==========================================

@login_required
def delete_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if leave.applicant != request.user and not request.user.is_staff:

        messages.error(
            request,
            "Permission denied."
        )

        return redirect("my_leaves")

    if request.method == "POST":

        leave.delete()

        messages.success(
            request,
            "Leave deleted successfully."
        )

        if request.user.is_staff:

            return redirect("leave_list")

        return redirect("my_leaves")

    return render(
        request,
        "leaves/delete_leave.html",
        {
            "leave": leave
        }
    )


# ==========================================
# APPROVE LEAVE
# ==========================================

@login_required
@admin_required
def approve_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    leave.status = "APPROVED"

    leave.save()

    messages.success(
        request,
        "Leave approved successfully."
    )

    return redirect("leave_list")


# ==========================================
# REJECT LEAVE
# ==========================================

@login_required
@admin_required
def reject_leave(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    leave.status = "REJECTED"

    leave.save()

    messages.success(
        request,
        "Leave rejected successfully."
    )

    return redirect("leave_list")