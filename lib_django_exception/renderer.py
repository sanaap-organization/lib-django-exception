from http import HTTPStatus

from rest_framework import renderers


class ProjectRender(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        view = renderer_context.get("view")

        # for skip exception handler, should set custom_exception_handler value to False in specific api
        if getattr(view, "custom_exception_handler", True):
            if response.status_code in range(200, 300):
                http_code_to_message = {v.value: v.description for v in HTTPStatus}
                new_response = {
                    "status_code": response.status_code,
                    "message": http_code_to_message[response.status_code],
                    "is_success": True,
                    "error": None,
                    "response": data,
                }
                return super(ProjectRender, self).render(
                    new_response, accepted_media_type, renderer_context
                )
            elif response.status_code in range(400, 500) and not response.data.get("status_code", None):
                http_code_to_message = {v.value: v.description for v in HTTPStatus}
                new_response = {
                    "status_code": response.status_code,
                    "message": http_code_to_message[response.status_code],
                    "is_success": False,
                    "error": None,
                    "response": data,
                }
                return super(ProjectRender, self).render(
                    new_response, accepted_media_type, renderer_context
                )
        return super(ProjectRender, self).render(
            response.data, accepted_media_type, renderer_context
        )
