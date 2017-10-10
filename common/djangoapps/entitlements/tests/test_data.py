"""
Test the Data Aggregation Layer for Course Entitlements.
"""
import unittest
import uuid

import ddt
from django.conf import settings

from entitlements.models import CourseEntitlement
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from student.tests.factories import CourseEnrollmentFactory


@ddt.ddt
@unittest.skipUnless(settings.ROOT_URLCONF == 'lms.urls', 'Test only valid in lms')
class EntitlementDataTest(ModuleStoreTestCase):
    """
    Test course entitlement data aggregation.
    """
    USERNAME = "Bob"
    EMAIL = "bob@example.com"
    PASSWORD = "edx"

    def setUp(self):
        """Create a course and user, then log in. """
        super(EntitlementDataTest, self).setUp()
        self.course = CourseFactory.create()
        self.parent_course_uuid = uuid.uuid4()
        self.user = UserFactory.create(username=self.USERNAME, email=self.EMAIL, password=self.PASSWORD)
        self.client.login(username=self.USERNAME, password=self.PASSWORD)

    def _add_entitlement_for_user(self, course, user, parent_uuid):
        entitlement_data = {
            'user': user,
            'parent_course_uuid': parent_uuid,
            'expiration': '2017-09-14 11:47:58.000000',
            'mode': 'verified',
            'is_active': True
        }
        stored_entitlement, is_created = CourseEntitlement.update_or_create_new_entitlement(
            user,
            parent_uuid,
            entitlement_data
        )
        return stored_entitlement, is_created

    def test_get_entitlement_info(self):
        stored_entitlement, is_created = self._add_entitlement_for_user(self.course, self.user, self.parent_course_uuid)
        self.assertTrue(is_created)

        # Get the Entitlement and verify the data
        entitlement = CourseEntitlement.get_user_course_entitlement(self.user, self.parent_course_uuid)
        self.assertEqual(entitlement.parent_course_uuid, self.parent_course_uuid)
        self.assertEqual(entitlement.mode, 'verified')
        self.assertEqual(entitlement.is_active, True)
        self.assertIsNone(entitlement.enrollment_course)

    def test_get_course_entitlements(self):
        course2 = CourseFactory.create()

        stored_entitlement, is_created = self._add_entitlement_for_user(self.course, self.user, self.parent_course_uuid)
        self.assertTrue(is_created)

        course2_uuid = uuid.uuid4()
        stored_entitlement2, is_created2 = self._add_entitlement_for_user(course2, self.user, course2_uuid)
        self.assertTrue(is_created2)

        # Get the Entitlement and verify the data
        entitlement_list = CourseEntitlement.entitlements_for_user(self.user)

        self.assertEqual(2, len(entitlement_list))
        self.assertEqual(self.parent_course_uuid, entitlement_list[0].parent_course_uuid)
        self.assertEqual(course2_uuid, entitlement_list[1].parent_course_uuid)

    def test_set_enrollment(self):
        stored_entitlement, is_created = self._add_entitlement_for_user(self.course, self.user, self.parent_course_uuid)
        self.assertTrue(is_created)

        # Entitlement set not enroll the user in the Course run
        enrollment = CourseEnrollmentFactory(
            user=self.user,
            course_id=self.course.id,
            is_active=True,
            mode="verified",
        )
        CourseEntitlement.set_entitlement_enrollment(self.user, self.parent_course_uuid, enrollment)

        entitlement = CourseEntitlement.get_user_course_entitlement(self.user, self.parent_course_uuid)
        self.assertIsNotNone(entitlement.enrollment_course)

    def test_remove_enrollment(self):
        stored_entitlement, is_created = self._add_entitlement_for_user(self.course, self.user, self.parent_course_uuid)
        self.assertTrue(is_created)

        # Entitlement set not enroll the user in the Course run
        enrollment = CourseEnrollmentFactory(
            user=self.user,
            course_id=self.course.id,
            is_active=True,
            mode="verified",
        )
        CourseEntitlement.set_entitlement_enrollment(self.user, self.parent_course_uuid, enrollment)

        entitlement = CourseEntitlement.get_user_course_entitlement(self.user, self.parent_course_uuid)
        self.assertIsNotNone(entitlement.enrollment_course)

        CourseEntitlement.remove_entitlement_enrollment(self.user, self.parent_course_uuid)
        entitlement = CourseEntitlement.get_user_course_entitlement(self.user, self.parent_course_uuid)
        self.assertIsNone(entitlement.enrollment_course)
