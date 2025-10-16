from django.db.models import TextChoices
from django.utils.translation import gettext as _

class ErrorMessagesCons(TextChoices):
    # basics
    unique = "This field must be unique.", _("This field must be unique.")
    required = "This field is required.", _("This field is required.")
    does_not_exist = "Object does not exist.", _("Object does not exist.")
    invalid = "This field is not valid.", _("This field is not valid.")
