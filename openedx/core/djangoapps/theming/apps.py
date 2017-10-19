
from django.apps import AppConfig
from django.conf import settings
from openedx.core.djangoapps.theming.core import enable_theming


class ThemingConfig(AppConfig):
    name = 'theming'
    verbose_name = "Theming"

    def ready(self):
        # Comprehensive theming needs to be set up before django startup,
        # because modifying django template paths after startup has no effect.
        if settings.ENABLE_COMPREHENSIVE_THEMING:
            enable_theming()
