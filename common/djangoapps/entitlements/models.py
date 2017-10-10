from django.db import models
from django.contrib.auth.models import User
from course_modes.models import CourseMode


class CourseEntitlement(models.Model):
    """
    Represents a Student's Entitlement to a Course Run for a given Course.
    """

    user = models.ForeignKey(User)

    parent_course_uuid = models.UUIDField(primary_key=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)

    updated = models.DateTimeField(auto_now=True)
    # The date that an enrollment must be applied by
    expiration = models.DateTimeField(null=False)

    # The mode of the Course that will be applied
    mode = models.CharField(default=CourseMode.DEFAULT_MODE_SLUG, max_length=100)

    # The ID of the course enrollment for this Entitlement
    # if NULL the entitlement is not in use
    enrollment_course = models.ForeignKey('student.CourseEnrollment', null=True)

    is_active = models.BooleanField(default=1)

    @classmethod
    def entitlements_for_user(cls, user):
        """
        Retrieve all the Entitlements for a User

        Arguments:
            user: A Django User object identifying the current user

        Returns:
            All of the Entitlements for the User
        """
        return cls.objects.filter(user=user)

    @classmethod
    def get_user_course_entitlement(cls, user, parent_course_uuid):
        """
        Retrieve The entitlement for the given parent course id if it exists for the User

        Arguments:
            user: A Django User object identifying the current user
            parent_course_uuid(string): The parent course uuid

        Returns:
            The single entitlement for the requested parent course id
        """
        return cls.objects.filter(user=user, parent_course_uuid=parent_course_uuid).first()

    @classmethod
    def update_or_create_new_entitlement(cls, user, parent_course_id, entitlement_data):
        """
        Updates or creates a new Course Entitlement

        Arguments:
            user: A Django User object identifying the current user
            parent_course_id(string): The parent course id string\
            entitlement_data(dict): The dictionary containing all the data for the entitlement
                e.g. entitlement_data = {
                        'user': user,
                        'parent_course_uuid': parent_course_id,
                        'enroll_end_date': '2017-09-14 11:47:58.000000',
                        'mode': 'verified',
                        'is_active': True
                    }

        Returns:
            stored_entitlement: The new or updated CourseEntitlement object
            is_created (bool): Boolean representing whether or not the Entitlement was created or updated
        """
        stored_entitlement, is_created = cls.objects.update_or_create(
            user=user,
            parent_course_uuid=parent_course_id,
            defaults=entitlement_data
        )
        return stored_entitlement, is_created

    @classmethod
    def set_entitlement_enrollment(cls, user, parent_course_id, course_run_enrollment):
        """
        Sets the enrollment course for a given entitlement

        Arguments:
            user: A Django User object identifying the current user
            parent_course_id(string): The parent course id string\
            course_run_enrollment (CourseEnrollment): The CourseEnrollment object to store
        """
        return cls.objects.filter(
            user=user,
            parent_course_uuid=parent_course_id
        ).update(enrollment_course_id=course_run_enrollment)

    @classmethod
    def remove_entitlement_enrollment(cls, user, parent_course_id):
        """
        Removes the enrollment course for a given entitlement

        Arguments:
            user: A Django User object identifying the current user
            parent_course_id(string): The parent course id string\
        """
        return cls.objects.filter(
            user=user,
            parent_course_uuid=parent_course_id
        ).update(enrollment_course_id=None)
