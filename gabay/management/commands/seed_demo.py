"""Create dummy accounts and data for trying the system. Safe to run more than once."""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from gabay.models import Attendance, Grade, ParentLink, Section, Student, Subject, User

PASSWORD = "gabay123"


class Command(BaseCommand):
    help = "Create demo users (password gabay123), students, grades, and attendance. Dummy data only."

    def handle(self, *args, **options):
        def user(username, role, first, last):
            u, created = User.objects.get_or_create(
                username=username, defaults={"role": role, "first_name": first, "last_name": last})
            if created:
                u.set_password(PASSWORD)
                u.save()
                u.apply_role_defaults()
            return u

        nanay = user("nanay", User.Role.PARENT, "Elena", "Cruz")
        tatay = user("tatay", User.Role.PARENT, "Ramon", "Reyes")
        user("sir", User.Role.TEACHER, "Mario", "Santos")
        adviser = user("maam", User.Role.ADVISER, "Luz", "Bautista")
        user("principal", User.Role.PRINCIPAL, "Rosa", "Garcia")

        Section.objects.get_or_create(name="Rizal", grade_level=7, defaults={"adviser": adviser})
        maria, _ = Student.objects.get_or_create(
            lrn="111111111111", defaults={"first_name": "Maria", "last_name": "Cruz", "grade_level": 7, "section": "Rizal"})
        jose, _ = Student.objects.get_or_create(
            lrn="222222222222", defaults={"first_name": "Jose", "last_name": "Reyes", "grade_level": 7, "section": "Rizal"})

        ParentLink.objects.link_parent(nanay.id, maria.id, "Mother", consent=True)
        ParentLink.objects.link_parent(nanay.id, jose.id, "Aunt", consent=False)  # no consent: stays hidden
        ParentLink.objects.link_parent(tatay.id, jose.id, "Father", consent=True)

        math, _ = Subject.objects.get_or_create(name="Mathematics")
        eng, _ = Subject.objects.get_or_create(name="English")
        for student, base in ((maria, 40), (jose, 44)):
            Grade.objects.get_or_create(student=student, subject=math, quarter=2, component="quiz",
                                        title="Quiz 1", defaults={"score": base, "highest_possible_score": 50})
            Grade.objects.get_or_create(student=student, subject=eng, quarter=2, component="exam",
                                        title="Midterm", defaults={"score": base + 3, "highest_possible_score": 60})
        today = date.today()
        Attendance.objects.get_or_create(student=maria, subject=math, date=today, period=1, defaults={"status": "absent"})
        Attendance.objects.get_or_create(student=maria, subject=eng, date=today - timedelta(days=1), period=2, defaults={"status": "late"})
        Attendance.objects.get_or_create(student=jose, subject=math, date=today, period=1, defaults={"status": "present"})

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Logins (password gabay123): nanay, tatay (parents), sir, maam (staff), principal."))
