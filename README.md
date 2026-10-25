# AI College Campus Management — Smart Campus ERP

A comprehensive college campus management system built with Django.

## Project Structure

```
AI-COLLEGE-CAMPUS-MANAGEMENT/
├── backend/                  # Django application (deployed on Render)
│   ├── manage.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── Procfile
│   ├── config/               # Django project settings & URL config
│   ├── accounts/             # User authentication & management
│   ├── students/             # Student profiles & management
│   ├── teachers/             # Teacher profiles & management
│   ├── departments/          # Department management
│   ├── courses/              # Course management & materials
│   ├── attendance/           # Attendance tracking
│   ├── qr_attendance/        # QR-based attendance
│   ├── assignments/          # Assignment management
│   ├── exams/                # Exam scheduling
│   ├── results/              # Result management
│   ├── leaves/               # Leave management
│   ├── notes/                # Notes & study materials
│   ├── announcements/        # Announcements
│   ├── timetable/            # Timetable management
│   ├── dashboard/            # Dashboard views
│   ├── templates/            # Django HTML templates (frontend UI)
│   └── static/               # CSS, JavaScript, images
├── frontend/                 # Frontend documentation
│   └── README.md             # Explains the Django template architecture
└── README.md                 # This file
```

## Tech Stack

- **Backend**: Django 6.0 (Python 3.13)
- **Frontend**: Django Templates + Bootstrap 5.3.3 + Custom CSS/JS
- **Database**: PostgreSQL (production) / SQLite (development)
- **Static Files**: Whitenoise
- **Server**: Gunicorn

## Deployment — Render

The entire application (backend + frontend templates) is deployed on Render as a single web service.

### Render Settings

| Setting              | Value                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| **Root Directory**   | `backend`                                                                                      |
| **Runtime**          | Python 3                                                                                       |
| **Build Command**    | `pip install -r requirements.txt`                                                              |
| **Start Command**    | `python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application` |

### Environment Variables (Render)

| Variable                | Description                          | Example                                         |
| ----------------------- | ------------------------------------ | ------------------------------------------------ |
| `SECRET_KEY`            | Django secret key                    | *(generate a strong random key)*                 |
| `DEBUG`                 | Debug mode                           | `False`                                          |
| `DATABASE_URL`          | PostgreSQL connection string         | `postgres://user:pass@host:5432/dbname`          |
| `ALLOWED_HOSTS`         | Comma-separated hostnames            | `your-app.onrender.com`                          |
| `CSRF_TRUSTED_ORIGINS`  | Comma-separated origins              | `https://your-app.onrender.com`                  |
| `EMAIL_HOST_USER`       | SMTP email username                  | `your-email@gmail.com`                           |
| `EMAIL_HOST_PASSWORD`   | SMTP email password / app password   | *(your app password)*                            |
| `SITE_URL`              | Public URL of the application        | `https://your-app.onrender.com`                  |
| `RENDER`                | Render platform flag                 | `true`                                           |

### Database

Attach a **PostgreSQL** database in Render. The `DATABASE_URL` environment variable will be set automatically by Render when you link the database to your web service.

## Local Development

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Features

- **Multi-role Authentication** — Admin, Teacher, Student
- **Student Management** — Profiles, enrollment, import/export
- **Teacher Management** — Profiles, course assignments
- **Department Management** — Create, update, import
- **Course Management** — Courses, materials, enrollment
- **Attendance Tracking** — Session-based + QR code attendance
- **Assignment Management** — Create, submit, grade
- **Exam Management** — Scheduling, duty assignment
- **Result Management** — Marks, marksheets, toppers
- **Leave Management** — Apply, approve, history
- **Notes & Materials** — Upload, share, download
- **Announcements** — Create, broadcast
- **Timetable** — Create, view by role
- **Dashboard** — Role-specific dashboards with analytics
- **Activity Logs** — Login/logout tracking
- **Password Reset** — Email OTP-based reset
