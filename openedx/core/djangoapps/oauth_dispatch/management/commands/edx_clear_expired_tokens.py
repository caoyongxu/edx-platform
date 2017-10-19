from __future__ import unicode_literals

import logging
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from oauth2_provider.models import AccessToken, Grant, RefreshToken
from oauth2_provider.settings import oauth2_settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Clear expired access tokens and refresh tokens for DOT"

    def add_arguments(self, parser):
        parser.add_argument('--batch_size',
                            action='store',
                            dest='batch_size',
                            type=int,
                            default=1000,
                            help='Maximum number of database rows to delete per query. '
                                 'This helps avoid locking the database when deleting large amounts of data.')

    def clear_table_data(self, query_set, batch_size, model):
        while query_set.exists():
            qs = query_set[:batch_size]
            query_set = query_set[batch_size:] if query_set[batch_size:] else query_set
            history_batch = qs.values_list('id', flat=True)
            with transaction.atomic():
                model.objects.filter(pk__in=list(history_batch)).delete()

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        now = timezone.now()
        refresh_expire_at = None

        refresh_token_expire_seconds = oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS

        if refresh_token_expire_seconds:
            if not isinstance(refresh_token_expire_seconds, timedelta):
                try:
                    refresh_token_expire_seconds = timedelta(seconds=refresh_token_expire_seconds)
                except TypeError:
                    e = "REFRESH_TOKEN_EXPIRE_SECONDS must be either a timedelta or seconds"
                    raise ImproperlyConfigured(e)
            refresh_expire_at = now - refresh_token_expire_seconds

        if refresh_expire_at:
            query_set = RefreshToken.objects.filter(access_token__expires__lt=refresh_expire_at)
            message = 'Cleaning {} rows from {} table'.format(query_set.count(), RefreshToken.__name__)
            logger.info(message)
            self.clear_table_data(query_set, batch_size, RefreshToken)

            query_set = AccessToken.objects.filter(refresh_token__isnull=True, expires__lt=now)
            message = 'Cleaning {} rows from {} table'.format(query_set.count(), AccessToken.__name__)
            logger.info(message)
            self.clear_table_data(query_set, batch_size, AccessToken)

            query_set = Grant.objects.filter(expires__lt=now)
            message = 'Cleaning {} rows from {} table'.format(query_set.count(), Grant.__name__)
            logger.info(message)
            self.clear_table_data(query_set, batch_size, Grant)
