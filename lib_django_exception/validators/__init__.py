import re

from django.core.validators import BaseValidator
from django.core.validators import RegexValidator
from django.http import QueryDict
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator as RestUniqueValidator, qs_exists

from lib_django_exception.exceptions import CustomValidationError


class PhoneNumberValidator(RegexValidator):
    regex = r"^0\d{10}$"
    message = _("Phone number is not valid.")


@deconstructible
class NationalCodeValidator:
    message = _("National code is not valid.")
    code = "invalid"

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, national_code):
        if not re.match(r"^\d{10}$", national_code):
            raise CustomValidationError(self.message, code=self.code)

        check = int(national_code[9])
        sum_val = sum(int(national_code[x]) * (10 - x) for x in range(9))
        remainder = sum_val % 11

        if remainder < 2:
            if check != remainder:
                raise CustomValidationError(self.message, code=self.code)
        elif check != 11 - remainder:
            raise CustomValidationError(self.message, code=self.code)


class UniqueValidator(RestUniqueValidator):
    message = _("%(field_name)s field must be unique.")

    def __call__(self, value, serializer_field):
        # Determine the underlying model field name. This may not be the
        # same as the serializer field name if `source=<>` is set.
        field_name = serializer_field.source_attrs[-1]
        # Determine the existing instance, if this is an update operation.
        instance = getattr(serializer_field.parent, "instance", None)

        queryset = self.queryset
        queryset = self.filter_queryset(value, queryset, field_name)
        queryset = self.exclude_current_instance(queryset, instance)
        if qs_exists(queryset):
            raise CustomValidationError(
                self.message, code="unique", params={"field_name": field_name}
            )


@deconstructible
class QueryParameterValidator(BaseValidator):
    code = "invalid_query_parameter"
    message = _("Query parameter is not valid.")

    def __init__(
            self,
            limit_value: list,
            required: bool = True,
            allow_null: bool = False,
            allow_blank: bool = False,
    ):
        """
        :param limit_value: list of parameters name which needs validation
        :param required: check if parameter is sent
        :param allow_null: check parameter nullable
        :param allow_blank: check parameter blank string
        """
        if isinstance(limit_value, str):
            self.limit_value = [limit_value]
        elif isinstance(limit_value, tuple):
            self.limit_value = list(limit_value)
        else:
            self.limit_value = limit_value
        self.required = required
        self.allow_null = allow_null
        self.allow_blank = allow_blank

    def __call__(self, value: QueryDict):
        """
        :param value: request.GET
        :return:
        """
        cleaned = self.clean(value)
        limit_value = (
            self.limit_value() if callable(self.limit_value) else self.limit_value
        )
        for parameter in limit_value:
            params = {"limit_value": parameter, "show_value": cleaned, "value": value}
            if self.compare(cleaned, parameter):
                raise CustomValidationError(self.message, code=self.code, params=params)

    def compare(self, value: dict, parameter):
        if self.required:
            if parameter not in value.keys():
                self.message = _(f"{parameter} Query parameter is required.")
                return True
        if not self.allow_null:
            if (
                    value.get(parameter, None) is None
                    or value.get(parameter, None) == "null"
            ):
                self.message = _(f"{parameter} Query parameter may not be null.")
                return True
        if not self.allow_blank:
            if value.get(parameter, "") == "":
                self.message = _(f"{parameter} Query parameter may not be blank.")
                return True
        return False

    def clean(self, value: QueryDict):
        """
        :param value: request.GET
        :return: convert request.GET OrderedDict to dict
        """
        value = value.dict()
        return value
