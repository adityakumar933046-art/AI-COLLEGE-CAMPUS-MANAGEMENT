from django.db.models import Count, Avg, Q, Min, Max
from students.models import StudentProfile
from attendance.models import Attendance
from results.models import Result
from assignments.models import Assignment
from courses.models import Course
from departments.models import Department

def get_all_student_attendance_stats(user):
    """Compute deterministic attendance percentage for all students."""
    students = StudentProfile.objects.select_related('user', 'department')
    if user.role == "STUDENT":
        students = students.filter(user=user)

    stats = []
    for st in students:
        records = Attendance.objects.filter(student=st)
        total = records.count()
        present = records.filter(status="PRESENT").count()
        late = records.filter(status="LATE").count()
        absent = records.filter(status="ABSENT").count()
        pct = round(((present + (late * 0.5)) / total * 100), 2) if total > 0 else 0.00
        
        stats.append({
            "id": st.id,
            "full_name": st.user.get_full_name() or st.user.username,
            "roll_no": st.roll_no,
            "department": st.department.name if st.department else "N/A",
            "semester": st.semester,
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "percentage": pct
        })
    return stats

def get_low_attendance_students(user, threshold=75.0):
    all_stats = get_all_student_attendance_stats(user)
    low_students = [s for s in all_stats if s["percentage"] < threshold]
    low_students.sort(key=lambda x: x["percentage"])
    
    total_count = len(all_stats)
    low_count = len(low_students)
    low_pct = round((low_count / total_count * 100), 1) if total_count > 0 else 0.0
    
    return {
        "threshold": threshold,
        "total_students": total_count,
        "low_attendance_count": low_count,
        "low_attendance_percentage": low_pct,
        "students": low_students
    }

def compare_attendance_stats(user, name1, name2):
    all_stats = get_all_student_attendance_stats(user)
    
    st1 = next((s for s in all_stats if name1.lower() in s["full_name"].lower()), None) or (all_stats[0] if all_stats else None)
    st2 = next((s for s in all_stats if name2.lower() in s["full_name"].lower() and s != st1), None) or (all_stats[1] if len(all_stats) > 1 else st1)
    
    if not st1 or not st2:
        return {"error": "Insufficient student records for comparison."}
    
    diff = round(abs(st1["percentage"] - st2["percentage"]), 2)
    better = st1 if st1["percentage"] > st2["percentage"] else (st2 if st2["percentage"] > st1["percentage"] else None)
    
    return {
        "student1": st1,
        "student2": st2,
        "percentage_difference": diff,
        "higher_student": better["full_name"] if better else "Equal"
    }

def get_student_academic_summary(user, student_name=None):
    all_stats = get_all_student_attendance_stats(user)
    
    if student_name:
        st_stat = next((s for s in all_stats if student_name.lower() in s["full_name"].lower() or student_name.lower() in str(s["roll_no"]).lower()), None)
    else:
        st_stat = all_stats[0] if all_stats else None
        
    if not st_stat:
        return {"error": f"Student record for '{student_name}' not found."}
        
    st_profile = StudentProfile.objects.filter(id=st_stat["id"]).first()
    
    # Results CGPA
    res_qs = Result.objects.filter(student=st_profile)
    results_count = res_qs.count()
    cgpa = round(sum(r.marks for r in res_qs) / results_count, 2) if results_count > 0 else 8.5
    
    # Pending Assignments
    pending_assigns = Assignment.objects.count()
    
    return {
        "student_id": st_profile.id,
        "full_name": st_stat["full_name"],
        "roll_no": st_stat["roll_no"],
        "department": st_stat["department"],
        "semester": st_stat["semester"],
        "attendance_percentage": st_stat["percentage"],
        "total_classes": st_stat["total"],
        "present_classes": st_stat["present"],
        "absent_classes": st_stat["absent"],
        "cgpa": cgpa,
        "published_results": results_count,
        "pending_assignments": pending_assigns
    }

def get_department_attendance_analytics(user):
    all_stats = get_all_student_attendance_stats(user)
    dept_map = {}
    
    for s in all_stats:
        d = s["department"]
        if d not in dept_map:
            dept_map[d] = []
        dept_map[d].append(s["percentage"])
        
    dept_summary = []
    for d_name, pcts in dept_map.items():
        avg_pct = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
        dept_summary.append({
            "department": d_name,
            "student_count": len(pcts),
            "average_attendance": avg_pct
        })
        
    dept_summary.sort(key=lambda x: x["average_attendance"], reverse=True)
    return {"departments": dept_summary}
