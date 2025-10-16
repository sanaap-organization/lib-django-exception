from typing import ClassVar, Optional

from django.db.models import ProtectedError
from django.utils.encoding import force_str
from django.utils.translation import activate, get_language
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict


class ExceptionClass:
    code: Optional[str] = None
    default_code: ClassVar[Optional[str]] = None

    def get_codes(self) -> Optional[str]:
        if self.code:
            return self.code
        elif self.default_code:
            return self.default_code
        return None


class ProtectedObjectException(ExceptionClass, ProtectedError):
    default_type: ClassVar[str] = "invalid_request"
    default_code: ClassVar[str] = "protected_error"
    status_code: ClassVar[int] = status.HTTP_409_CONFLICT
    default_detail: ClassVar[str] = _(
        "Requested operation cannot be completed because a related object is protected."
    )

    def __init__(self, msg, protected_objects):
        self.detail = force_str(msg or self.default_detail)
        super().__init__(msg, protected_objects)


class ErrorDetail(str):
    """
    A string-like object that can additionally have a code.
    """

    code = None
    params = {}

    def __new__(cls, string, code=None, params={}):
        self = super().__new__(cls, string % params)
        self.code = code
        self.params = params
        return self

    def __eq__(self, other):
        result = super().__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        try:
            return result and self.code == other.code
        except AttributeError:
            return result

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __repr__(self):
        return "ErrorDetail(string=%r, code=%r, params=%r)" % (str(self), self.code, self.params)

    def __hash__(self):
        return hash(str(self))


def _get_error_details(data, default_code=None, params=None, translate=False):
    """
    Descend into a nested data structure, forcing any
    lazy translation strings or strings into `ErrorDetail`.
    """
    if isinstance(data, (list, tuple)):
        ret = [_get_error_details(item, default_code, params, translate) for item in data]
        if isinstance(data, ReturnList):
            return ReturnList(ret, serializer=data.serializer)
        return ret
    elif isinstance(data, dict):
        ret = {key: _get_error_details(value, default_code, params, translate) for key, value in data.items()}
        if isinstance(data, ReturnDict):
            return ReturnDict(ret, serializer=data.serializer)
        return ret

    if isinstance(data, str) and translate:
        current_language = get_language()
        activate("fa")
        data = _(data)
        activate(current_language)

    text = force_str(data)
    code = getattr(data, "code", default_code)
    return ErrorDetail(text, code, params)


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'
    default_params = {}

    def __init__(self, detail=None, code=None, params=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if params is None:
            params = self.default_params

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, str):
            detail = [detail % params]
        elif isinstance(detail, ValidationError):
            detail = detail.detail
        elif isinstance(detail, (list, tuple)):
            final_detail = []
            for detail_item in detail:
                if isinstance(detail_item, ValidationError):
                    final_detail += detail_item.detail
                else:
                    final_detail += [detail_item % params if isinstance(detail_item, str) else detail_item]
            detail = final_detail
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = _get_error_details(detail, code)


class CustomValidationError(ValidationError):
    def __init__(self, detail=None, code=None, params=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if params is None:
            params = self.default_params

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if isinstance(detail, str):
            detail = [detail]
        elif isinstance(detail, ValidationError):
            detail = detail.detail
        elif isinstance(detail, (list, tuple)):
            final_detail = []
            for detail_item in detail:
                if isinstance(detail_item, ValidationError):
                    final_detail += detail_item.detail
                else:
                    final_detail += [detail_item if isinstance(detail_item, str) else detail_item]
            detail = final_detail
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        # Ensure the language is activated
        self.detail = _get_error_details(detail, code, params)
        self.fa_detail = _get_error_details(detail, code, params, translate=True)