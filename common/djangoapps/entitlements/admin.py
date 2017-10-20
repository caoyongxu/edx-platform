from django.contrib import admin
from .models import CourseEntitlement


@admin.register(CourseEntitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'course_uuid',
                    'created',
                    'updated',
                    'expired_at',
                    'mode',
                    'enrollment_course_run')
