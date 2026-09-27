from django.urls import path
from . import views

urlpatterns = [
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/analytics/", views.performance_analytics, name="performance_analytics"),
    path("teacher/students/", views.student_list, name="student_list"),
    path("teacher/students/delete/<int:student_id>/", views.delete_student, name="delete_student"),
    path("teacher/enter-marks/", views.enter_marks, name="enter_marks"),
    path("teacher/enter-marks/<int:student_id>/", views.enter_marks, name="enter_marks_existing"),
    path("teacher/download/<int:student_id>/", views.download_result_pdf, name="download_result_pdf_teacher"),

    path("student/", views.student_result, name="student_result"),
    path("student/download/", views.download_result_pdf, name="download_result_pdf"),
]
