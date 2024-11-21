
from unittest.mock import patch
from django.test import TestCase
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from clothes_shop.models.user import User
from clothes_shop.services.email_service import EmailService
import os


class EmailServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="securepassword123",
            is_active=False,
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.fixed_token = "test-token" 
        self.base_url = os.getenv("CONFIRMATION_URL", "http://127.0.0.1:8081")

    @patch("clothes_shop.services.email_service.send_mail")
    @patch("clothes_shop.services.email_service.token_generator")
    def test_send_confirmation_email_success(self, mock_token_generator, mock_send_mail):
        mock_token_generator.make_token.return_value = self.fixed_token
        mock_send_mail.return_value = 1

        EmailService.send_email(self.user, email_type="confirmation")

        expected_subject = "Confirm your email"
        expected_message = (
            f"Please click the following link to verify your email: "
            f"{self.base_url}/api/signup/account-confirm-email/{self.uid}/{self.fixed_token}/"
        )
        expected_from_email = settings.DEFAULT_FROM_EMAIL
        expected_recipient_list = [self.user.email]

        mock_send_mail.assert_called_once_with(
            expected_subject,
            expected_message,
            expected_from_email,
            expected_recipient_list,
        )

    @patch("clothes_shop.services.email_service.send_mail")
    @patch("clothes_shop.services.email_service.token_generator")
    @patch.dict(os.environ, {"CONFIRMATION_URL": "http://testserver.com"})
    def test_send_confirmation_email_with_env_url(
        self, mock_token_generator, mock_send_mail
    ):
        mock_token_generator.make_token.return_value = self.fixed_token 
        mock_send_mail.return_value = 1

        EmailService.send_email(self.user, email_type="confirmation")

        expected_url = (
            f"http://testserver.com/api/signup/account-confirm-email/{self.uid}/{self.fixed_token}/"
        )

        args, kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, args[1])
