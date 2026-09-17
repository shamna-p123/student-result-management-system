# Student Result Management System

Django + SQLite project with role-based login (Teacher / Student), marks entry,
automatic grade/percentage/pass-fail calculation, and PDF report card download.

## 1. Setup

```bash
# (recommended) create a virtual environment first
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser      # create your admin login
python manage.py seed_demo_data       # creates subjects + a demo teacher & student
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

## 2. Demo logins (created by `seed_demo_data`)

| Role    | Username  | Password         |
|---------|-----------|------------------|
| Teacher | teacher1  | teacherpass123   |
| Student | student1  | studentpass123   |

## 3. How roles work

- Django's built-in `auth.User` model is used for login.
- Two Groups exist: **Teacher** and **Student**.
- After login, `accounts/views.py -> post_login_redirect` checks the user's
  group and sends them to the right dashboard.
- Superusers (`createsuperuser`) are always treated as teachers.

## 4. Adding a new student login

Student accounts need a `User` + a linked `Student` profile (roll number, name, class).
Easiest way for now: **Django admin** (`/admin/`):

1. Log in to `/admin/` with your superuser account.
2. Under **Users**, add a new user, and add them to the **Student** group.
3. Under **Results > Students**, create a `Student` row linking that user,
   with a unique roll number.

Once that exists, the teacher can enter marks against that roll number from
the **Enter Marks** screen, and the student can log in to see their result.

Adding a new teacher is the same, except add them to the **Teacher** group instead
(no `Student` profile needed).

## 5. App structure

```
accounts/    -> login, logout, role-based redirect
results/     -> Student, Subject, Result, ResultSummary models
                teacher dashboard, marks entry, student result view, PDF export
```

## 6. Grade & Pass/Fail logic (results/models.py -> calculate_grade / recalculate_summary)

- Percentage = (total marks obtained / total max marks) * 100
- Grade bands: A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥40, else F
- Status = **Fail** if overall percentage < 40% OR any single subject is
  below 40% of its max marks; otherwise **Pass**.
- Edit `calculate_grade()` and the status logic in `recalculate_summary()`
  in `results/models.py` to match your institution's actual grading rules.

## 7. PDF generation

Uses `xhtml2pdf`, which renders a plain HTML+CSS template
(`results/templates/results/report_pdf.html`) straight into a PDF — no
external binaries needed, works cross-platform.

Note: `xhtml2pdf` only supports basic/legacy CSS (tables, simple styling) —
no flexbox or CSS grid — so the PDF template is intentionally kept simple
and separate from the on-screen templates.

Both the teacher (per student) and the logged-in student (their own report)
can trigger this via the "Download PDF" buttons, which hit:
- `/results/teacher/download/<student_id>/` (teacher)
- `/results/student/download/` (student, their own result only)

## 8. Switching from SQLite to MySQL

1. `pip install mysqlclient`
2. In `result_management/settings.py`, replace the `DATABASES` dict with the
   MySQL block that's already commented out right below it.
3. Create the database in MySQL (`CREATE DATABASE result_management;`).
4. Re-run `python manage.py migrate`.

No other code changes are needed — the whole app uses Django's ORM.

## 9. Security note before deploying anywhere real

- Change `SECRET_KEY` in `settings.py`.
- Set `DEBUG = False` and set `ALLOWED_HOSTS` properly.
- This demo uses Django's default session-based auth, which is fine for a
  college project; don't reuse the demo passwords anywhere real.
