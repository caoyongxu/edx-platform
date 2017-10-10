# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0013_delete_historical_enrollment_records'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseEntitlement',
            fields=[
                ('parent_course_uuid', models.UUIDField(serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('expiration', models.DateTimeField()),
                ('mode', models.CharField(default=b'audit', max_length=100)),
                ('is_active', models.BooleanField(default=1)),
                ('enrollment_course', models.ForeignKey(to='student.CourseEnrollment', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
