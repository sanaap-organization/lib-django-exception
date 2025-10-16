from setuptools import setup, find_packages
setup(
    name='lib-django-exception',
    version='0.2.0',
    author='Sanaap Organization',
    author_email='',
    packages=find_packages(include=['lib_django_exception', 'lib_django_exception.*']),
    description='lib-django-exception',
    install_requires=[
        'Django>=3.2',
        'djangorestframework>=3.12'
    ],
)
