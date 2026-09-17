from django.db import models
from django.contrib.auth.models import User

class Semester(models.Model):
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.FloatField()
    max_marks = models.FloatField(default=100)

    class Meta:
        unique_together = ("student", "subject")

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.marks}/{self.max_marks}"


class ResultSummary(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="summary")
    total_marks = models.FloatField()
    total_max_marks = models.FloatField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=5)
    status = models.CharField(max_length=10)  # Pass / Fail
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.student.name}: {self.percentage:.2f}% ({self.status})"


def calculate_grade(percentage):
    """Simple grade boundary logic — adjust to match your institution's scale."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 40:
        return "D"
    return "F"


def recalculate_summary(student):
    """Recompute and save the ResultSummary for a student from their Result rows."""
    results = Result.objects.filter(student=student)
    total = sum(r.marks for r in results)
    total_max = sum(r.max_marks for r in results)
    percentage = (total / total_max * 100) if total_max else 0
    grade = calculate_grade(percentage)
    # Fail overall if percentage is below the pass threshold OR any single subject is failed.
    subject_failed = any(r.marks < (0.4 * r.max_marks) for r in results)
    status = "Fail" if (percentage < 40 or subject_failed) else "Pass"

    summary, _ = ResultSummary.objects.update_or_create(
        student=student,
        defaults={
            "total_marks": total,
            "total_max_marks": total_max,
            "percentage": percentage,
            "grade": grade,
            "status": status,
        },
    )
    return summary
