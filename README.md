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
