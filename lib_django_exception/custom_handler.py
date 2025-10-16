from http import HTTPStatus

from rest_framework.views import exception_handler as rest_exception_handler

from .handler import exception_handler


def custom_exception_handler(exc, context):
    # handle_exception
    view = context.get("view")
    if getattr(view, "custom_exception_handler", True):
        response = exception_handler(exc, context)
        if response is not None:
            http_code_to_message = {v.value: v.description for v in HTTPStatus}
            new_response = {
                "status_code": response.status_code,
                "message": http_code_to_message[response.status_code],
                "is_success": False,
                "error": response.data,
                "response": None,
            }
            print(new_response)
            response.data = new_response
        return response
    response = rest_exception_handler(exc, context)
    return response
