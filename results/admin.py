from django.contrib import admin
from .models import Student, Subject, Result, ResultSummary


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("roll_number", "name", "student_class", "user")
    search_fields = ("roll_number", "name")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "marks", "max_marks")
    list_filter = ("subject",)


@admin.register(ResultSummary)
class ResultSummaryAdmin(admin.ModelAdmin):
    list_display = ("student", "total_marks", "percentage", "grade", "status")
