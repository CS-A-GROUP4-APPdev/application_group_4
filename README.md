## Gabay: Student Progress and Attendance Monitoring System

Backend built with Python, Django, and Django REST Framework.

### Setup (PostgreSQL, the main database)
```
createdb gabay                      # or create the database in pgAdmin
python -m venv venv
venv\Scripts\activate               # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # dummy accounts and data (optional)
python manage.py runserver
```
Defaults: database `gabay`, user `gabay`, password `gabay`, host `127.0.0.1`, port `5432`.
Override with `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
The user needs permission to create databases so that `manage.py test` can make a test database.

### Quick development without PostgreSQL (SQLite fallback)
```
set DB_ENGINE=sqlite                # Windows (use export on macOS/Linux)
python manage.py migrate
python manage.py runserver
```
SQLite uses the ORM instead of the stored procedures. Use PostgreSQL before merging to `develop`.

### Run tests
```
python manage.py test                       # PostgreSQL
set DB_ENGINE=sqlite & python manage.py test   # SQLite fallback
```

### Demo logins (after `python manage.py seed_demo`, password `gabay123`)
| Username | Role | Lands on |
|---|---|---|
| `nanay` | Parent | Parent Portal (sees Maria only: link to Jose has no consent) |
| `tatay` | Parent | Parent Portal (sees Jose) |
| `sir` | Teacher | Staff Dashboard |
| `maam` | Adviser | Staff Dashboard |
| `principal` | Principal | Staff Dashboard (+ School overview) |

### Creating accounts
1. `python manage.py createsuperuser` (once), then open http://127.0.0.1:8000/admin/ and log in.
2. **Users > Add user**: enter a username and password, choose the **Role**, save.

The role sets everything else automatically (`User.apply_role_defaults` in `gabay/models/user.py`):

| Role | Admin-site access | Group |
|---|---|---|
| Parent/Guardian, Student | No | Parent / Student |
| Subject Teacher, Adviser, Principal | No | Teacher / Adviser / Principal (with that role's permissions) |
| Admin | Yes (staff + superuser) | Admin |

Staff status, superuser status and groups are shown read-only on the user page; change the role instead.
For a parent, also add the child under **Students** and a **Parent link** with **Consent given** ticked.

### Project structure (MVC, as in the proposal section 2.3)
```
config/                 settings.py, urls.py (the router: every route in one file)
gabay/
  models/               MODELS: one file per model (user, student, parent_link, section, subject, grade, attendance)
  controllers/          CONTROLLERS: auth, parent_portal, grade, attendance, report
  views/                VIEWS: one per controller (auth_view, parent_portal_view, ...), the HTML templates,
                        and frontend/ (the React app, the main parent-facing view)
  services/             SERVICES: smart logic (summary generator, pass calculator, ...). Reserved, not built yet.
libraries/              shared helper (stored_procedure.py)
assets/                 stored_procedure/*.sql
tests/                  test_models, one test file per controller, test_project_structure
```

#### The proposal and where each part lives
| Proposal layer | Proposal contents | In the code |
|---|---|---|
| Models | User, Student, ParentLink, Section, Subject, Grade, Attendance, ... | `gabay/models/`, one file per model. Built: the 7 listed. Not built yet: AbsenceReason, RiskFlag, ActionPlan, Goal, Consent, Notification, ConferenceSlot, Acknowledgment |
| Controllers | Auth, Grade, Attendance, ParentPortal, ActionPlan, Conference, Report | `gabay/controllers/`. Built: `auth`, `grade`, `attendance`, `parent_portal`, `report` (staff dashboard and school overview). Not built yet: ActionPlan, Conference |
| Views | Parent dashboard, reports, ... | `gabay/views/`, one view file per controller, with the HTML templates. The React app in `gabay/views/frontend/` is the main parent dashboard |
| Services | summaryGenerator, passScoreCalculator, patternDetector, riskScorer, qrVerifier | `gabay/services/` is created but empty: none are built yet |

#### What each layer does
| Layer | Job | Must NOT |
|---|---|---|
| Model | Data and rules: tables, queries, the privacy rule, stored procedure calls | know about requests, pages, or JSON |
| View | How data is shown: page rendering, JSON serializers | query the database, call a controller |
| Controller | Takes the request, checks the role, asks the Model, gives the result to the View | build database queries itself |
| Service | Smart logic as plain Python | touch requests, pages, or queries |

The flow follows the proposal ("controllers handle requests and call the model and services"): the **Controller** calls the Model,
receives the data, and passes it to the View. A Model never calls a View.

The React app is the View layer itself (`gabay/views/frontend/`): pages, components and dummy data only, with no MVC of its own.
See its own [README](gabay/views/frontend/README.md) for how to run it.

`tests/test_project_structure.py` fails if a layer does another layer's job (for example a controller that builds
its own query), so the structure stays MVC as the project grows.

**Adding a feature:** add `gabay/models/<model>.py` (and import it in `gabay/models/__init__.py`), then
`gabay/controllers/<name>_controller.py` and `gabay/views/<name>_view.py`, and list its routes in `config/urls.py`.

### Pages
| Path | Who can open it |
|---|---|
| `/login/`, `/logout/` (POST) | Everyone |
| `/portal/` | Parents only |
| `/staff/` | Teacher, adviser, principal, admin |
| `/staff/overview/` | Principal and admin only |
| `/students/<id>/` | Anyone logged in, but only for students they may view (else 404) |
| `/api/students/`, `/api/students/<id>/`, `.../grades/`, `.../attendance/` | Logged in; same visibility rule |
| `/admin/` | Django admin |

A logged-in user who opens a page their role cannot use sees the custom 403 page
(`gabay/templates/auth/403.html`). Anonymous users are sent to the login page.

### The privacy rule (one function)
`Student.objects.visible_to(user)` in `gabay/models/student.py` is the only place that decides which students a user may see.
Every controller must use it. Do not query `Student.objects` directly to show student data.
- Parent: only linked students WITH consent. No consent means nothing is shown.
- Student: own record only.
- Teacher, adviser, principal, admin, superuser: all students (until sections and teacher assignments are linked to students).
- Not logged in or inactive: nobody.

### Models
`User`, `Student`, `ParentLink` (consent), `Section`, `Subject`, `Grade` (score is checked to be 0 up to the highest score),
`Attendance` (database `UNIQUE` on student, subject, date, period).

The Django app label is still `users` (see `gabay/apps.py`), so table names, migrations and `AUTH_USER_MODEL` did not change.

### Stored procedure and function (PostgreSQL)
SQL is in `assets/stored_procedure/` and installed by `gabay/migrations/0002_stored_procedures.py`:
- `sp_link_parent(parent_id, student_id, relationship, consent)` PROCEDURE
- `fn_students_of_parent(parent_id)` FUNCTION (consent must be given)

Models call them through `libraries/stored_procedure.py`; on SQLite the same methods use the ORM.

### Branches
- `main`: stable
- `develop`: integration and QA testing
- feature branches: one per task, merged by pull request
