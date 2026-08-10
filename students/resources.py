from import_export import resources
from .models import StudentProfile


class StudentProfileResource(resources.ModelResource):

    class Meta:
        model = StudentProfile
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ("roll_no",)

        fields = (
            "roll_no",
            "admission_no",
            "department",
            "semester",
            "section",
            "batch",
            "academic_year",
            "phone",
            "alternate_phone",
            "gender",
            "blood_group",
            "father_name",
            "mother_name",
            "guardian_phone",
            "address",
            "city",
            "state",
            "pincode",
            "cgpa",
            "status",
        )