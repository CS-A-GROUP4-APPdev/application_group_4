"""Shared test data used by several module tests."""
from datetime import date

from gabay.models import Attendance, Grade, ParentLink, Section, Student, Subject, User



class PrivacyFixtureMixin:
    def setUp(self):
        mk = lambda name, role: User.objects.create_user(name, password="pw12345!", role=role)
        self.nanay = mk("nanay", User.Role.PARENT)
        self.tatay = mk("tatay", User.Role.PARENT)
        self.teacher = mk("sir", User.Role.TEACHER)
        self.adviser = mk("maam", User.Role.ADVISER)
        self.principal = mk("principal", User.Role.PRINCIPAL)
        self.admin_user = mk("admin1", User.Role.ADMIN)
        self.stu_user = mk("maria", User.Role.STUDENT)

        self.maria = Student.objects.create(lrn="111111111111", first_name="Maria", last_name="Cruz",
                                            grade_level=7, section="Rizal", user=self.stu_user)
        self.jose = Student.objects.create(lrn="222222222222", first_name="Jose", last_name="Reyes",
                                           grade_level=7, section="Rizal")
        self.ana = Student.objects.create(lrn="333333333333", first_name="Ana", last_name="Lim",
                                          grade_level=8, section="Luna")
        ParentLink.objects.link_parent(self.nanay.id, self.maria.id, "Mother", consent=True)
        ParentLink.objects.link_parent(self.nanay.id, self.jose.id, "Aunt", consent=False)  # no consent
        ParentLink.objects.link_parent(self.tatay.id, self.jose.id, "Father", consent=True)

        math = Subject.objects.create(name="Mathematics")
        for s in (self.maria, self.jose, self.ana):
            Grade.objects.create(student=s, subject=math, quarter=1, component="quiz",
                                 score=40, highest_possible_score=50)
            Attendance.objects.create(student=s, subject=math, date=date.today(), period=1, status="absent")

    def login(self, user):
        self.client.force_login(user)
