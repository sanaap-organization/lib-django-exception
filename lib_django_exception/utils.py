from enum import Enum
from typing import Any, Callable

from django.utils.encoding import force_str
from django.utils.translation import gettext as _, get_language, activate

def ensure_string(func: Callable) -> Callable:
    def function_wrapper(*args, **kwargs) -> str:
        return_value: Any = func(*args, **kwargs)
        if isinstance(return_value, Enum):
            return force_str(return_value.value)
        return force_str(return_value)

    return function_wrapper

def translate_text(text: str) -> str:
    current_language = get_language()
    activate("fa")
    data = _(text)
    activate(current_language)
    return data