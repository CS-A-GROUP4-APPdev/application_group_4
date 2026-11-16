"""Guards for the project structure.

1. Database compatibility: the restructure must not change tables or migrations,
   so existing databases keep working.
2. MVC layering (proposal section 2.3): the app is split into the layers
   gabay/models, gabay/views, gabay/controllers and gabay/services, and each layer
   stays in its own job. These checks read the source code, so a layer that starts
   doing another layer's work fails the test suite.

   - Model      : data and rules. Knows nothing about requests, HTML, or JSON output.
   - View       : how data is shown. Never queries the database or calls a controller.
   - Controller : receives the request, asks the Model, hands the result to the View.
                  Never builds database queries itself.
   - Service    : smart logic. Plain Python: no requests, pages, or queries.
"""
import ast
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from gabay.models import Attendance, Grade, ParentLink, Section, Student, Subject, User

APP = Path(settings.BASE_DIR) / "gabay"


def layer_files(layer):
    return sorted(p for p in (APP / layer).glob("*.py") if p.name != "__init__.py")


# Query-building calls that belong in a Model (manager/queryset method), not in a controller.
ORM_QUERY_CALLS = {
    "filter", "exclude", "get", "all", "annotate", "aggregate", "values", "values_list", "order_by",
    "create", "get_or_create", "update_or_create", "bulk_create", "select_related", "prefetch_related", "raw",
}


# ------------------------------------------------------------------ the rules (pure functions on source text)
def _imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def _is_layer_import(name, layer):
    """True for ``gabay.<layer>`` or anything inside it."""
    return name == f"gabay.{layer}" or name.startswith(f"gabay.{layer}.")


def check_model(source):
    problems = []
    for name in _imports(ast.parse(source)):
        if name.startswith(("django.shortcuts", "django.http", "django.template", "rest_framework")):
            problems.append(f"Model imports {name}: models must not know about requests, pages, or JSON output")
        if any(_is_layer_import(name, layer) for layer in ("controllers", "views", "services")):
            problems.append(f"Model imports {name}: models must not depend on controllers, views, or services")
    return problems


def check_view(source):
    tree, problems = ast.parse(source), []
    for name in _imports(tree):
        if _is_layer_import(name, "controllers"):
            problems.append(f"View imports {name}: views must not depend on a controller")
        if name.startswith("django.db"):
            problems.append(f"View imports {name}: views must not touch the database")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "objects":
            problems.append(f"View uses .objects (line {node.lineno}): views must not query the database")
    return problems


def check_controller(source):
    tree, problems = ast.parse(source), []
    for name in _imports(tree):
        if name.startswith("django.db"):
            problems.append(f"Controller imports {name}: put database work in the Model")
    for node in ast.walk(tree):
        if (isinstance(node, ast.Attribute) and node.attr in ORM_QUERY_CALLS
                and isinstance(node.value, ast.Attribute) and node.value.attr == "objects"):
            problems.append(
                f"Controller calls .objects.{node.attr}() (line {node.lineno}): "
                "add a method to the Model's manager and call that instead")
    return problems


def check_service(source):
    problems = []
    for name in _imports(ast.parse(source)):
        if name.startswith(("django.shortcuts", "django.http", "django.db", "rest_framework")):
            problems.append(f"Service imports {name}: services are plain logic, no requests or queries")
        if any(_is_layer_import(name, layer) for layer in ("controllers", "views")):
            problems.append(f"Service imports {name}: services must not depend on controllers or views")
    return problems


# ------------------------------------------------------------------ the project must follow the rules
class MvcLayeringTests(SimpleTestCase):
    def test_the_four_layers_exist(self):
        for layer in ("models", "views", "controllers", "services"):
            self.assertTrue((APP / layer / "__init__.py").exists(), f"gabay/{layer}/ is missing")

    def test_every_controller_has_a_view(self):
        # Auth controller -> auth_view, Grade controller -> grade_view, ...
        for path in layer_files("controllers"):
            name = path.stem.removesuffix("_controller")
            self.assertTrue((APP / "views" / f"{name}_view.py").exists(), f"{path.name} has no views/{name}_view.py")

    def _check_layer(self, layer, check):
        files = layer_files(layer)
        self.assertTrue(files, f"no files found in gabay/{layer}/")
        for path in files:
            self.assertEqual(check(path.read_text(encoding="utf-8")), [], f"{layer}/{path.name}")

    def test_models_stay_in_their_layer(self):
        self._check_layer("models", check_model)

    def test_views_stay_in_their_layer(self):
        self._check_layer("views", check_view)

    def test_controllers_stay_in_their_layer(self):
        self._check_layer("controllers", check_controller)

    def test_services_stay_in_their_layer(self):
        for path in layer_files("services"):  # empty for now: nothing built yet
            self.assertEqual(check_service(path.read_text(encoding="utf-8")), [], path.name)


class MvcCheckersCatchViolationsTests(SimpleTestCase):
    """The checks above are only useful if they really fail on bad code."""

    def test_controller_with_its_own_query_is_caught(self):
        bad = "def page(request):\n    return Attendance.objects.filter(date=today).count()\n"
        self.assertEqual(len(check_controller(bad)), 1)

    def test_controller_using_a_model_method_is_fine(self):
        good = "def page(request):\n    return Student.objects.visible_to(request.user)\n"
        self.assertEqual(check_controller(good), [])

    def test_controller_importing_the_database_layer_is_caught(self):
        self.assertEqual(len(check_controller("from django.db.models import Count\n")), 1)

    def test_model_returning_a_page_is_caught(self):
        self.assertEqual(len(check_model("from django.shortcuts import render\n")), 1)

    def test_model_depending_on_a_view_is_caught(self):
        self.assertEqual(len(check_model("from gabay.views.parent_portal_view import StudentSerializer\n")), 1)

    def test_view_that_queries_is_caught(self):
        self.assertEqual(len(check_view("def show():\n    return Student.objects.all()\n")), 1)

    def test_service_that_queries_is_caught(self):
        self.assertEqual(len(check_service("from django.db import connection\n")), 1)

    def test_view_depending_on_a_controller_is_caught(self):
        self.assertEqual(len(check_view("from gabay.controllers.auth_controller import home\n")), 1)


# ------------------------------------------------------------------ database compatibility
class DatabaseCompatibilityTests(TestCase):
    def test_all_models_are_registered_in_admin(self):
        for model in (Section, Subject, Grade, Attendance, Student, ParentLink, User):
            self.assertTrue(admin.site.is_registered(model), model.__name__)

    def test_app_label_and_table_names_are_unchanged(self):
        # The stored procedures and every existing database use these exact names.
        expected = {
            User: "users_user", Student: "users_student", ParentLink: "users_parentlink",
            Section: "users_section", Subject: "users_subject", Grade: "users_grade",
            Attendance: "users_attendance",
        }
        for model, table in expected.items():
            self.assertEqual(model._meta.app_label, "users", model.__name__)
            self.assertEqual(model._meta.db_table, table, model.__name__)
        self.assertEqual(settings.AUTH_USER_MODEL, "users.User")

    def test_every_model_is_defined_in_the_models_layer(self):
        # No stray models: each one lives in gabay/models/<name>.py, one file per model.
        for model in apps.get_app_config("users").get_models():
            parts = model.__module__.split(".")
            self.assertEqual(parts[:2], ["gabay", "models"], f"{model.__name__} is defined in {model.__module__}")
            snake = re.sub(r"(?<!^)(?=[A-Z])", "_", model.__name__).lower()  # ParentLink -> parent_link
            self.assertEqual(parts[2], snake, f"{model.__name__} should be in gabay/models/{snake}.py")

    def test_models_and_migrations_are_in_sync(self):
        # Fails if a model was changed without a migration (or the other way round).
        call_command("makemigrations", check=True, dry_run=True, verbosity=0)
