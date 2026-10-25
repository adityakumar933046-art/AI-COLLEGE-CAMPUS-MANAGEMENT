import pandas as pd

from .services import create_student


def import_students(file):

    df = pd.read_excel(file)

    credentials = []

    for _, row in df.iterrows():

        student = create_student(

            first_name=row["First Name"],

            last_name=row["Last Name"],

            email=row["Email"],

            roll_no=row["Roll No"],

            department=row["Department"],

            semester=row["Semester"],

            phone=row["Phone"],

        )

        credentials.append({

            "username": student["username"],

            "password": student["password"]

        })

    return credentials