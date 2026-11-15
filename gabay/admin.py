"""Django admin (back-office). Gathers the registrations for every module's models."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from gabay.models import Attendance, Grade, ParentLink, Section, Student, Subject, User


@admin.register(User)
class GabayUserAdmin(UserAdmin):
    _role = ("Gabay", {"fields": ("role",), "description": "Choose the role: staff access, group and permissions are set automatically."})
    fieldsets = UserAdmin.fieldsets + (_role,)
    add_fieldsets = UserAdmin.add_fieldsets + (_role,)
    list_display = ("username", "first_name", "last_name", "role", "is_active")
    list_filter = UserAdmin.list_filter + ("role",)

    # The role decides these, so they are shown but not editable (see User.apply_role_defaults).
    readonly_fields = ("is_staff", "is_superuser", "groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # New account, or the role was changed: apply the role's permissions.
        # An existing account saved without a role change (e.g. one made with createsuperuser) is left alone.
        if not change or "role" in form.changed_data:
            obj.apply_role_defaults()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("lrn", "last_name", "first_name", "grade_level", "section")
    search_fields = ("lrn", "last_name", "first_name")
    list_filter = ("grade_level", "section")


@admin.register(ParentLink)
class ParentLinkAdmin(admin.ModelAdmin):
    list_display = ("parent", "student", "relationship", "consent_given")
    list_filter = ("consent_given",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "grade_level", "adviser")
    list_filter = ("grade_level",)
    search_fields = ("name",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "quarter", "component", "title", "score", "highest_possible_score")
    list_filter = ("quarter", "component", "subject")
    search_fields = ("student__lrn", "student__last_name", "student__first_name")
    autocomplete_fields = ("student", "subject")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "date", "period", "status")
    list_filter = ("status", "date", "subject")
    search_fields = ("student__lrn", "student__last_name", "student__first_name")
    date_hierarchy = "date"
    autocomplete_fields = ("student", "subject")
