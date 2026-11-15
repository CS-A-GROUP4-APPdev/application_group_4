from django.apps import AppConfig


class GabayConfig(AppConfig):
    name = "gabay"
    # IMPORTANT: the label stays "users". Existing databases, migrations, the stored
    # procedures (users_student, users_parentlink, ...) and AUTH_USER_MODEL = "users.User"
    # all use this label. Changing it would force everyone to rebuild their database.
    label = "users"
