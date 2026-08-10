def sidebar_items(user):

    if not user.is_authenticated:

        return []

    if user.role == "ADMIN":

        return [

            ("Dashboard","/admin-dashboard/"),

            ("Students","/manage-students/"),

            ("Teachers","/manage-teachers/"),

            ("Departments","/departments/"),

            ("Courses","/manage-courses/"),

            ("Attendance","/attendance/"),

            ("Assignments","/assignments/"),

            ("Results","/results/"),

            ("Notes","/notes/"),

            ("Announcements","/announcements/"),

            ("Logout","/logout/")

        ]

    elif user.role == "TEACHER":

        return [

            ("Dashboard","/teacher-dashboard/"),

            ("Students","/teacher/students/"),

            ("Attendance","/attendance/"),

            ("Assignments","/assignments/"),

            ("Notes","/notes/"),

            ("Results","/results/"),

            ("Logout","/logout/")

        ]

    return [

        ("Dashboard","/student-dashboard/"),

        ("Attendance","/attendance/"),

        ("Assignments","/assignments/"),

        ("Results","/results/"),

        ("Notes","/notes/"),

        ("Leaves","/leaves/"),

        ("Timetable","/timetable/"),

        ("Logout","/logout/")

    ]