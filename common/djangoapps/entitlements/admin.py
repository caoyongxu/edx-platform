from django.contrib import admin
from .models import CourseEntitlement


@admin.register(CourseEntitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent_course_uuid', 'expiration',
                    'mode', 'enrollment_course', 'is_active')
