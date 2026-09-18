from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Student, Subject, Result, ResultSummary, Semester, recalculate_summary


def is_teacher(user):
    return user.is_superuser or user.groups.filter(name="Teacher").exists()


def is_student(user):
    return user.groups.filter(name="Student").exists()


# ---------- TEACHER VIEWS ----------

@login_required
def teacher_dashboard(request):
    if not is_teacher(request.user):
        messages.error(request, "You are not authorized to view that page.")
        return redirect("post_login_redirect")

    semesters = Semester.objects.all().order_by("name")
    students = Student.objects.select_related("summary").order_by("roll_number")

    return render(
        request,
        "results/teacher_dashboard.html",
        {
            "students": students,
            "semesters": semesters,
        }
    )

@login_required
def enter_marks(request, student_id=None):
    if not is_teacher(request.user):
        messages.error(request, "You are not authorized to view that page.")
        return redirect("post_login_redirect")

    subjects = Subject.objects.all()
    student = None
    existing_marks = {}

    # Editing an existing student
    if student_id:
        student = get_object_or_404(Student, id=student_id)
        existing_marks = {
            r.subject_id: r.marks
            for r in Result.objects.filter(student=student)
        }

    if request.method == "POST":
        roll_number = request.POST.get("roll_number", "").strip()
        name = request.POST.get("name", "").strip()
        student_class = request.POST.get("student_class", "").strip()

        # Create a new student automatically
        if not student:

            if not roll_number:
                messages.error(request, "Please enter the student roll number.")
                return render(
                    request,
                    "results/enter_marks.html",
                    {
                        "subjects": subjects,
                        "existing_marks": existing_marks,
                    }
                )

            if not name:
                messages.error(request, "Please enter the student name.")
                return render(
                    request,
                    "results/enter_marks.html",
                    {
                        "subjects": subjects,
                        "existing_marks": existing_marks,
                    }
                )

            # Maximum 100 students
            if Student.objects.count() >= 100:
                messages.error(
                    request,
                    "Maximum student limit of 100 has been reached."
                )
                return render(
                    request,
                    "results/enter_marks.html",
                    {
                        "subjects": subjects,
                        "existing_marks": existing_marks,
                    }
                )

            # Check duplicate roll number
            if Student.objects.filter(roll_number=roll_number).exists():
                messages.error(
                    request,
                    f"Student with roll number {roll_number} already exists. "
                    "Please use the Edit Mark option."
                )
                return render(
                    request,
                    "results/enter_marks.html",
                    {
                        "subjects": subjects,
                        "existing_marks": existing_marks,
                    }
                )

            # Check duplicate username
            if User.objects.filter(username=roll_number).exists():
                messages.error(
                    request,
                    f"The username {roll_number} already exists."
                )
                return render(
                    request,
                    "results/enter_marks.html",
                    {
                        "subjects": subjects,
                        "existing_marks": existing_marks,
                    }
                )

            # Create login account
            user = User.objects.create_user(
                username=roll_number,
                password=roll_number,
                first_name=name,
            )

            # Add Student role
            student_group, _ = Group.objects.get_or_create(
                name="Student"
            )
            user.groups.add(student_group)

            # Create Student profile
            student = Student.objects.create(
                user=user,
                roll_number=roll_number,
                name=name,
                student_class=student_class,
            )

            messages.info(
                request,
                f"New student created successfully. "
                f"Username: {roll_number} | Password: {roll_number}"
            )

        # Update student details
        if name:
            student.name = name

        if student_class:
            student.student_class = student_class

        student.save()

        # Save marks
        for subj in subjects:
            raw = request.POST.get(
                f"marks_{subj.id}",
                ""
            ).strip()

            if raw == "":
                continue

            try:
                marks = float(raw)
            except ValueError:
                continue

            max_marks = 60

            marks = max(
                0,
                min(marks, max_marks)
            )

            Result.objects.update_or_create(
                student=student,
                subject=subj,
                defaults={
                    "marks": marks,
                    "max_marks": max_marks,
                },
            )

        # Calculate result summary
        recalculate_summary(student)

        messages.success(
            request,
            f"Marks saved successfully for "
            f"{student.name} ({student.roll_number})."
        )

        return redirect("teacher_dashboard")

    return render(
        request,
        "results/enter_marks.html",
        {
            "subjects": subjects,
            "student": student,
            "existing_marks": existing_marks,
        }
    )
# ---------- PERFORMANCE ANALYTICS ----------

@login_required
def performance_analytics(request):
    if not is_teacher(request.user):
        messages.error(request, "You are not authorized to view that page.")
        return redirect("post_login_redirect")

    students = Student.objects.select_related("summary").all()
    summaries = ResultSummary.objects.select_related("student").all()

    # ---------- OVERALL SUMMARY ----------

    total_students = students.count()
    passed_students = summaries.filter(status="Pass").count()
    failed_students = summaries.filter(status="Fail").count()

    pass_percentage = (
        (passed_students / total_students) * 100
        if total_students > 0 else 0
    )

    percentages = [
        s.percentage for s in summaries
        if s.percentage is not None
    ]

    class_average = (
        sum(percentages) / len(percentages)
        if percentages else 0
    )

    highest_percentage = max(percentages) if percentages else 0
    lowest_percentage = min(percentages) if percentages else 0

    # ---------- GRADE DISTRIBUTION ----------

    grade_distribution = {}

    for summary in summaries:
        grade = summary.grade or "N/A"

        if grade not in grade_distribution:
            grade_distribution[grade] = 0

        grade_distribution[grade] += 1

    grade_data = sorted(grade_distribution.items())

    # ---------- SUBJECT-WISE ANALYSIS ----------

    subjects = Subject.objects.all()

    subject_data = []
    subject_chart_data = []
    subject_pass_fail_data = []

    for subject in subjects:

        results = Result.objects.filter(subject=subject)

        total_marks = sum(r.marks for r in results)
        result_count = results.count()

        average = (
            total_marks / result_count
            if result_count > 0 else 0
        )

        # Pass mark = 30 out of 60
        passed = results.filter(marks__gte=30).count()
        failed = results.filter(marks__lt=30).count()

        subject_data.append({
            "name": subject.name,
            "average": round(average, 2),
            "passed": passed,
            "failed": failed,
        })

        subject_chart_data.append({
            "name": subject.name,
            "average": round(average, 2),
        })

        subject_pass_fail_data.append({
            "name": subject.name,
            "passed": passed,
            "failed": failed,
        })

    context = {
        # Overall statistics
        "total_students": total_students,
        "passed_students": passed_students,
        "failed_students": failed_students,
        "pass_percentage": round(pass_percentage, 2),
        "class_average": round(class_average, 2),
        "highest_percentage": round(highest_percentage, 2),
        "lowest_percentage": round(lowest_percentage, 2),

        # Grade analysis
        "grade_data": grade_data,

        # Subject analysis
        "subject_data": subject_data,
        "subject_chart_data": subject_chart_data,
        "subject_pass_fail_data": subject_pass_fail_data,

        # Student analysis
        "students": students,
    }

    return render(
        request,
        "results/performance_analytics.html",
        context
    )
# ---------- STUDENT VIEWS ----------

@login_required
def student_result(request):
    if not hasattr(request.user, "student_profile"):
        messages.error(request, "No student profile linked to this account.")
        return redirect("login")

    student = request.user.student_profile
    results = Result.objects.filter(student=student).select_related("subject")
    summary = ResultSummary.objects.filter(student=student).first()

    return render(request, "results/student_result.html",
                   {"student": student, "results": results, "summary": summary})


# ---------- PDF EXPORT (shared by teacher + student) ----------

@login_required
def download_result_pdf(request, student_id=None):
    if student_id:
        # Teacher downloading a specific student's report
        if not is_teacher(request.user):
            messages.error(request, "You are not authorized to do that.")
            return redirect("post_login_redirect")
        student = get_object_or_404(Student, id=student_id)
    else:
        # Student downloading their own report
        if not hasattr(request.user, "student_profile"):
            messages.error(request, "No student profile linked to this account.")
            return redirect("login")
        student = request.user.student_profile

    results = Result.objects.filter(student=student).select_related("subject")
    summary = ResultSummary.objects.filter(student=student).first()

    if not summary:
        messages.error(request, "No results have been entered for this student yet.")
        return redirect("post_login_redirect")

    template = get_template("results/report_pdf.html")
    html = template.render({"student": student, "results": results, "summary": summary})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.roll_number}_report_card.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("An error occurred while generating the PDF.", status=500)
    return response
