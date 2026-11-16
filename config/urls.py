"""URL configuration for the Gabay project: the router (the old index.php).

Each controller's addresses are listed here, one block per controller, so this
file shows every route in the system at a glance.
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from gabay.controllers import (
    attendance_controller, auth_controller, grade_controller, parent_portal_controller, report_controller,
)

auth_urls = [
    path('', auth_controller.home, name='home'),
    path('login/', auth_controller.LoginController.as_view(), name='login'),
    path('logout/', auth_controller.LogoutController.as_view(), name='logout'),
]

parent_portal_urls = [
    path('portal/', parent_portal_controller.parent_portal, name='index'),
    path('students/<int:pk>/', parent_portal_controller.student_detail, name='student_detail'),
]

report_urls = [
    path('staff/', report_controller.staff_dashboard, name='dashboard'),
    path('staff/overview/', report_controller.staff_overview, name='overview'),
]

# JSON API, mounted under /api/
_students = DefaultRouter()
_students.register('students', parent_portal_controller.StudentApiController, basename='student')
api_urls = [
    *_students.urls,
    path('students/<int:pk>/grades/', grade_controller.StudentGradesApiController.as_view(), name='student-grades'),
    path('students/<int:pk>/attendance/', attendance_controller.StudentAttendanceApiController.as_view(),
         name='student-attendance'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('', include((auth_urls, 'auth'))),
    path('', include((parent_portal_urls, 'parent_portal'))),
    path('', include((report_urls, 'report'))),
]

# Custom 403 Forbidden page, shown when a logged-in user opens a page their role cannot use.
handler403 = 'gabay.controllers.auth_controller.forbidden'
