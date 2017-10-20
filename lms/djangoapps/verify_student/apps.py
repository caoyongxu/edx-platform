"""
Student Identity Verification Application Configuration
"""

from django.apps import AppConfig


class VerifyStudentConfig(AppConfig):
    """
    Application Configuration for verify_student.
    """
    name = 'verify_student'
    verbose_name = 'Student Identity Verification'

    def ready(self):
        """
        Connect signal handlers.
        """
        from .signals import handlers  # pylint: disable=unused-variable
