"""Django settings for tests."""

SECRET_KEY = "test-secret-key-for-djicons"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "djicons",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    },
]

USE_TZ = True

# djicons settings
DJICONS = {
    "DEFAULT_NAMESPACE": "ion",
    "AUTO_DISCOVER": False,  # Don't auto-discover in tests
    "MISSING_ICON_SILENT": True,
    "PACKS": [],  # No packs by default in tests
}
