"""
Tests for the Sending activation email celery tasks
"""

import mock
from boto.exception import NoAuthHandlerFound
from django.conf import settings
from django.test import TestCase
from student.tests.factories import CourseEnrollmentFactory
from lms.djangoapps.courseware.tests.factories import UserFactory
from opaque_keys.edx.keys import CourseKey
from student.tasks import send_activation_email, update_course_enrollment

TEST_EMAIL = "test@edx.org"


class SendActivationEmailTestCase(TestCase):
    """
    Test for send activation email to user
    """

    def setUp(self):
        """ Setup components used by each test."""
        super(SendActivationEmailTestCase, self).setUp()
        self.student = UserFactory()

    @mock.patch('time.sleep', mock.Mock(return_value=None))
    @mock.patch('student.tasks.log')
    @mock.patch('django.core.mail.send_mail', mock.Mock(side_effect=NoAuthHandlerFound))
    def test_send_email(self, mock_log):
        """
        Tests retries when the activation email doesn't send
        """
        from_address = 'task_testing@example.com'
        email_max_attempts = settings.RETRY_ACTIVATION_EMAIL_MAX_ATTEMPTS

        # pylint: disable=no-member
        send_activation_email.delay('Task_test', 'Task_test_message', from_address, self.student.email)

        # Asserts sending email retry logging.
        for attempt in range(email_max_attempts):
            mock_log.info.assert_any_call(
                'Retrying sending email to user {dest_addr}, attempt # {attempt} of {max_attempts}'.format(
                    dest_addr=self.student.email,
                    attempt=attempt,
                    max_attempts=email_max_attempts
                ))
        self.assertEquals(mock_log.info.call_count, 6)

        # Asserts that the error was logged on crossing max retry attempts.
        mock_log.error.assert_called_with(
            'Unable to send activation email to user from "%s" to "%s"',
            from_address,
            self.student.email,
            exc_info=True
        )
        self.assertEquals(mock_log.error.call_count, 1)


class MockSailthruResponse(object):
    """
    Mock object for SailthruResponse
    """

    def __init__(self, json_response, error=None, code=1):
        self.json = json_response
        self.error = error
        self.code = code

    def is_ok(self):
        """
        Return true of no error
        """
        return self.error is None

    def get_error(self):
        """
        Get error description
        """
        return MockSailthruError(self.error, self.code)


class MockSailthruError(object):
    """
    Mock object for Sailthru Error
    """

    def __init__(self, error, code=1):
        self.error = error
        self.code = code

    def get_message(self):
        """
        Get error description
        """
        return self.error

    def get_error_code(self):
        """
        Get error code
        """
        return self.code


class SailthruTests(TestCase):
    """
    Tests for the Sailthru tasks class.
    """

    def setUp(self):
        super(SailthruTests, self).setUp()
        self.course_id = CourseKey.from_string('edX/toy/2012_Fall')
        self.course_url = 'http://lms.testserver.fake/courses/edX/toy/2012_Fall/info'
        self.course_id2 = 'edX/toy/2016_Fall'
        self.course_url2 = 'http://lms.testserver.fake/courses/edX/toy/2016_Fall/info'

    @mock.patch('sailthru.sailthru_client.SailthruClient.purchase')
    @mock.patch('sailthru.sailthru_client.SailthruClient.api_get')
    @mock.patch('sailthru.sailthru_client.SailthruClient.api_post')
    def test_update_course_enrollment(self, mock_sailthru_api_post,
                                      mock_sailthru_api_get, mock_sailthru_purchase):
        """test update sailthru user record"""

        # create mocked Sailthru API responses
        mock_sailthru_api_post.return_value = MockSailthruResponse({'ok': True})
        mock_sailthru_api_get.return_value = MockSailthruResponse({'user': {"id": TEST_EMAIL, "fields": {"vars": 1}}})
        mock_sailthru_purchase.return_value = MockSailthruResponse({'ok': True})
        self.user = UserFactory()
        self.user.email = TEST_EMAIL
        CourseEnrollmentFactory(user=self.user, course_id=self.course_id)
        with mock.patch('student.tasks.build_course_url') as m:
            m.return_value = self.course_url
            update_course_enrollment(self.user, self.course_id, 'audit')
        item = [{
            'url': self.course_url,
            'price': 0,
            'qty': 1,
            'id': 'edX/toy/2012_Fall-audit',
            'title': 'Course edX/toy/2012_Fall mode: audit'
        }]
        mock_sailthru_purchase.assert_called_with(TEST_EMAIL, item, options={})
