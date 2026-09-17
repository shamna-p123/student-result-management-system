from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand

from results.models import Subject, Student, Result, ResultSummary, recalculate_summary


class Command(BaseCommand):
    help = "Creates MCA teacher, 60 students, 7 MCA subjects and sample marks."

    def handle(self, *args, **options):

        # ---------------------------------------------------------
        # 1. CREATE GROUPS
        # ---------------------------------------------------------
        teacher_group, _ = Group.objects.get_or_create(name="Teacher")
        student_group, _ = Group.objects.get_or_create(name="Student")

        # ---------------------------------------------------------
        # 2. REMOVE OLD DEMO DATA
        # ---------------------------------------------------------

        # Remove old demo student
        old_student_usernames = ["student1"]

        for username in old_student_usernames:
            try:
                user = User.objects.get(username=username)
                user.delete()
                self.stdout.write(
                    self.style.WARNING(f"Removed old demo student: {username}")
                )
            except User.DoesNotExist:
                pass

        # Remove old demo teacher
        try:
            old_teacher = User.objects.get(username="teacher1")
            old_teacher.delete()
            self.stdout.write(
                self.style.WARNING("Removed old demo teacher: teacher1")
            )
        except User.DoesNotExist:
            pass

        # Remove old school subjects
        old_subjects = [
            "Mathematics",
            "Science",
            "English",
            "Social Studies",
            "Computer Science",
        ]

        Subject.objects.filter(name__in=old_subjects).delete()

        # ---------------------------------------------------------
        # 3. MCA SUBJECTS
        # ---------------------------------------------------------

        subjects = [
            "Mathematical Foundations for Computing",
            "Digital Fundamentals & Computer Architecture",
            "Advanced Data Structures",
            "Advanced Software Engineering",
            "Programming Lab",
            "Web Programming Lab",
            "Data Structures Lab",
        ]

        subject_objects = []

        for subject_name in subjects:
            subject, _ = Subject.objects.get_or_create(
                name=subject_name
            )
            subject_objects.append(subject)

        # ---------------------------------------------------------
        # 4. CREATE TEACHER
        # ---------------------------------------------------------

        teacher_username = "MCA_Teacher"

        if not User.objects.filter(username=teacher_username).exists():

            teacher = User.objects.create_user(
                username=teacher_username,
                password=teacher_username,
                first_name="MCA",
                last_name="Teacher"
            )

            teacher.groups.add(teacher_group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Teacher login created -> "
                    f"username: {teacher_username} / "
                    f"password: {teacher_username}"
                )
            )

        else:
            self.stdout.write(
                f"Teacher account already exists: {teacher_username}"
            )

        # ---------------------------------------------------------
        # 5. STUDENT NAMES
        # ---------------------------------------------------------

        student_names = [
            "ABIDAMOL T K",
            "ABISHEK",
            "AHAMED SHADI",
            "AHAMED SWALIH M",
            "AKASH P",
            "AKHIL PREMAN",
            "AKHILA N",
            "ANAKHA K V",
            "ANASWARA P",
            "ANSHA GAFOOR",
            "APARNA T V",
            "ARATHI K",
            "ARJUN K P",
            "ASWINRAG K",
            "DANUSH DEVANANDAN",
            "FADLU RAHMAN K",
            "FARSEENA K",
            "FATHIMA RIFA",
            "FATHIMATH MUHSINA P",
            "FIDHA FATHIMA",
            "GAYATHRI T P",
            "HARSHIDA P",
            "HASNA P",
            "HENAN",
            "HISHA FADIYA A G",
            "HUDHA",
            "JASEEL NM",
            "JASNA JAMAL P",
            "KADEEJA NAISHA",
            "KRISHNAPRIYA",
            "KRISHNAPRIYA KP",
            "LIYANA",
            "MAHJABEEN P",
            "MAJIDA FARSANA",
            "MASOOD C",
            "MEHAJABINA P M",
            "MOHAMED NIHAL",
            "MOHAMMED JASIR M",
            "MOHAMMED RASHID T V",
            "MOHAMMED SAFVAN N",
            "MUFEENA THESNI P",
            "MUHAMMED ALTHAF O K",
            "MUHAMMED NADEEM",
            "MUHAMMED SANWEER K T",
            "NAHAN SHAWKKATHALI",
            "NAJA MUJEEB T",
            "NASEEBA U",
            "NASRIN KUNHIMOIDU",
            "NESLA UK",
            "NIHALA SHERIN VP",
            "RAHIL MUHAMMAD P V",
            "REVATHI R MENON",
            "SAHLA SHERIN",
            "SANA",
            "SANDRA VISMAYA C E",
            "SHAMNA P",
            "SUBITHA SUDHAKARAN",
            "SUHAILA NASREEN C",
            "THANSIYA NASRIN A",
            "THRISHNA P C",
        ]

        # ---------------------------------------------------------
        # 6. SAMPLE MARKS
        # ---------------------------------------------------------

        # Different marks for each student and subject.
        # Maximum mark for every subject = 60.

        base_marks = [
            [52, 48, 55, 50, 57, 54, 51],
            [45, 50, 47, 52, 49, 55, 48],
            [56, 54, 52, 57, 55, 53, 56],
            [41, 46, 44, 48, 50, 45, 43],
            [53, 51, 49, 54, 52, 56, 50],
            [47, 44, 51, 46, 55, 49, 52],
            [58, 55, 57, 54, 59, 56, 58],
            [50, 52, 48, 51, 53, 49, 54],
            [43, 47, 45, 42, 48, 50, 46],
            [55, 53, 56, 51, 54, 57, 52],
            [49, 46, 50, 48, 52, 51, 47],
            [57, 56, 54, 58, 55, 59, 57],
            [44, 42, 47, 45, 49, 46, 43],
            [51, 49, 53, 50, 55, 52, 54],
            [48, 50, 46, 52, 51, 47, 49],
            [54, 52, 55, 53, 57, 54, 56],
            [46, 45, 48, 44, 50, 47, 51],
            [52, 55, 50, 54, 53, 56, 52],
            [40, 43, 42, 45, 47, 44, 41],
            [56, 58, 55, 57, 59, 54, 58],
            [49, 51, 47, 50, 52, 48, 53],
            [53, 54, 52, 55, 51, 57, 54],
            [38, 41, 39, 43, 45, 42, 40],
            [47, 49, 45, 48, 50, 46, 51],
            [55, 52, 57, 54, 56, 58, 55],
            [50, 48, 52, 51, 54, 53, 49],
            [42, 45, 44, 46, 48, 43, 47],
            [58, 57, 56, 59, 55, 58, 57],
            [51, 53, 50, 52, 54, 51, 55],
            [46, 48, 45, 49, 47, 50, 44],
            [54, 55, 53, 56, 52, 57, 54],
            [49, 47, 51, 50, 53, 48, 52],
            [57, 54, 58, 55, 59, 56, 57],
            [44, 46, 42, 48, 45, 49, 43],
            [52, 50, 54, 53, 55, 51, 56],
            [48, 45, 50, 47, 52, 49, 51],
            [55, 57, 53, 56, 54, 58, 55],
            [41, 44, 43, 46, 48, 45, 42],
            [50, 52, 49, 51, 54, 53, 50],
            [56, 55, 57, 54, 58, 56, 59],
            [47, 49, 46, 50, 48, 51, 45],
            [53, 51, 55, 52, 54, 57, 53],
            [45, 43, 47, 44, 49, 46, 48],
            [58, 56, 59, 57, 55, 58, 56],
            [51, 50, 53, 49, 55, 52, 54],
            [43, 46, 42, 45, 47, 44, 48],
            [54, 53, 55, 52, 57, 56, 54],
            [48, 50, 47, 51, 49, 52, 46],
            [52, 54, 51, 53, 55, 50, 56],
            [46, 48, 44, 47, 50, 45, 49],
            [57, 55, 58, 56, 59, 57, 55],
            [49, 51, 50, 48, 53, 52, 54],
            [53, 52, 55, 54, 56, 51, 57],
            [42, 44, 41, 46, 48, 43, 45],
            [55, 56, 54, 57, 53, 58, 55],
            [50, 49, 52, 51, 54, 48, 53],
            [47, 45, 49, 46, 51, 48, 50],
            [58, 59, 57, 56, 55, 58, 59],
            [51, 53, 50, 54, 52, 55, 51],
            [54, 52, 56, 53, 55, 57, 54]
        ]

        # ---------------------------------------------------------
        # 7. CREATE 60 STUDENTS + MARKS
        # ---------------------------------------------------------

        for index, student_name in enumerate(student_names):

            number = index + 1

            username = f"MES25MCA{number:02d}"

            roll_number = username

            # Create student login
            user, created = User.objects.get_or_create(
                username=username
            )

            if created:
                user.set_password(username)
                user.first_name = student_name
                user.save()

            user.groups.add(student_group)

            # Create student profile
            student, _ = Student.objects.get_or_create(
                user=user,
                defaults={
                    "roll_number": roll_number,
                    "name": student_name,
                    "student_class": "MCA",
                }
            )

            # Update existing student details if necessary
            student.roll_number = roll_number
            student.name = student_name
            student.student_class = "MCA"
            student.save()

            # Add marks
            marks_for_student = base_marks[index]

            for subject, mark in zip(subject_objects, marks_for_student):

                Result.objects.update_or_create(
                    student=student,
                    subject=subject,
                    defaults={
                        "marks": mark,
                        "max_marks": 60,
                    }
                )

            # Calculate total, percentage, grade and status
            recalculate_summary(student)

            self.stdout.write(
                f"Created/updated {number:02d}: "
                f"{student_name} -> {username}"
            )

        # ---------------------------------------------------------
        # 8. FINISH
        # ---------------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "\nMCA project data created successfully!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Teacher username: MCA_Teacher"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Teacher password: MCA_Teacher"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Student usernames/passwords: MES25MCA01 to MES25MCA60"
            )
        )