
# Gabay: Student Progress and Attendance Monitoring System

Backend built with Python, Django, and Django REST Framework.

## Setup (Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/admin/ and log in.

## Setup (macOS/Linux)
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Run tests
```
python manage.py test
```

## Branches
- `main`: stable
- `develop`: integration and QA testing
- feature branches: one per task, merged by pull request

## First models (users app)
- `User`: custom user with a role (parent, student, teacher, adviser, principal, admin)
- `Student`: LRN, name, grade level, section
- `ParentLink`: links a parent to a student with relationship and consent

## Stored procedure and function (PostgreSQL)
Created by `users/migrations/0002_stored_procedures.py`:
- `sp_link_parent(parent_id, student_id, relationship, consent)` PROCEDURE: checks the user is a parent and the student exists, then inserts or updates the parent link.
- `fn_students_of_parent(parent_id)` FUNCTION: returns only the students a parent may see (consent must be given).

Views call them through `ParentLink.objects.link_parent(...)` and `Student.objects.for_parent(...)` (`users/managers.py`). On SQLite the same methods use the ORM instead.

### Run with PostgreSQL
```
createdb gabay            # or create the database in pgAdmin
set DB_ENGINE=postgres    # Windows (use export on macOS/Linux)
set DB_NAME=gabay
set DB_USER=gabay
set DB_PASSWORD=gabay
python manage.py migrate
python manage.py test
```

# application_group_4
 origin/develop
