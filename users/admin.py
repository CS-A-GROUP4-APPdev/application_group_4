from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ParentLink, Student, User


@admin.register(User)
class GabayUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Gabay", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Gabay", {"fields": ("role",)}),)
    list_display = ("username", "first_name", "last_name", "role", "is_active")
    list_filter = UserAdmin.list_filter + ("role",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("lrn", "last_name", "first_name", "grade_level", "section")
    search_fields = ("lrn", "last_name", "first_name")
    list_filter = ("grade_level", "section")


@admin.register(ParentLink)
class ParentLinkAdmin(admin.ModelAdmin):
    list_display = ("parent", "student", "relationship", "consent_given")
    list_filter = ("consent_given",)
