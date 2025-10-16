from typing import Dict

from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS: Dict = getattr(settings, "EXCEPTIONS_HOG", None)

DEFAULTS: Dict = {
    "EXCEPTION_REPORTING": "lib_django_exception.handler.exception_reporter",
    "ENABLE_IN_DEBUG": False,
    "NESTED_KEY_SEPARATOR": "__",
    "SUPPORT_MULTIPLE_EXCEPTIONS": False,
    "FARSI_EXCEPTION": True,
}

# List of settings that may be in string import notation.
# e.g. `exceptions_hog.lib_django_exception`
IMPORT_STRINGS = ("EXCEPTION_REPORTING",)

api_settings: APISettings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
