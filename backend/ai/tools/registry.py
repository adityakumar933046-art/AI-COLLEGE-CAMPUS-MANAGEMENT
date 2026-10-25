from .student_tools import search_student, get_student_profile
from .teacher_tools import search_teacher, get_teacher_profile
from .department_tools import search_department
from .course_tools import search_course
from .attendance_tools import get_student_attendance
from .result_tools import get_student_results
from .timetable_tools import get_timetable
from .leave_tools import get_leaves
from .content_tools import search_notes, search_announcements, search_assignments

READ_ONLY_TOOLS = {
    "search_student": search_student,
    "get_student_profile": get_student_profile,
    "search_teacher": search_teacher,
    "get_teacher_profile": get_teacher_profile,
    "search_department": search_department,
    "search_course": search_course,
    "get_student_attendance": get_student_attendance,
    "get_student_results": get_student_results,
    "get_timetable": get_timetable,
    "get_leaves": get_leaves,
    "search_notes": search_notes,
    "search_announcements": search_announcements,
    "search_assignments": search_assignments
}

TOOL_DECLARATIONS = [
    {
        "name": "search_student",
        "description": "Search for students by name, roll number, or admission number.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Student name or roll number"}
            }
        }
    },
    {
        "name": "get_student_profile",
        "description": "Get detailed profile information of a student.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "student_name": {"type": "STRING", "description": "Student name or roll number"}
            }
        }
    },
    {
        "name": "get_student_attendance",
        "description": "Get attendance percentage and statistics of a student.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "student_name": {"type": "STRING", "description": "Student name or roll number"}
            }
        }
    },
    {
        "name": "get_student_results",
        "description": "Get academic results and GPA of a student.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "student_name": {"type": "STRING", "description": "Student name or roll number"}
            }
        }
    },
    {
        "name": "get_timetable",
        "description": "Get class schedule timetable for student or teacher.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "day": {"type": "STRING", "description": "Day of the week (e.g. Monday)"}
            }
        }
    },
    {
        "name": "get_leaves",
        "description": "Get list of leave applications.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "status": {"type": "STRING", "description": "Leave status (PENDING, APPROVED, REJECTED)"}
            }
        }
    },
    {
        "name": "search_announcements",
        "description": "Search or view campus announcements.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Announcement topic or keyword"}
            }
        }
    }
]
