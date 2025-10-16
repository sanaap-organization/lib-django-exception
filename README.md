# lib-django-exception

## add required configurations to django settings.py

add this two line in REST_FRAMEWORK to settings

```
'EXCEPTION_HANDLER': 'lib_django_exception.custom_handler.custom_exception_handler'
'DEFAULT_RENDERER_CLASSES': ['lib_django_exception.renderer.ProjectRender']
```

add this config of your handler in settings
```
EXCEPTIONS_HOG = {
    "EXCEPTION_REPORTING": "lib_django_exception.handler.exception_reporter",
    "ENABLE_IN_DEBUG": False,
    "FARSI_EXCEPTION": True,
}
```