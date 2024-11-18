import os
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import logging

logger = logging.getLogger(__name__)

token_generator = PasswordResetTokenGenerator()


class EmailService:
    @staticmethod
    def send_email(user, email_type="confirmation"):
        try:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            if email_type == "confirmation":
                base_url = os.getenv("CONFIRMATION_URL", "http://127.0.0.1:8081")
                url = f"{base_url}/api/signup/account-confirm-email/{uid}/{token}/"
                subject = "Confirm your email"
                message = f"Please click the following link to verify your email: {url}"
            else:
                raise ValueError("Invalid email type specified")

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        except Exception as e:
            logger.error(f"Failed to send {email_type} email to {user.email}: {e}")
            raise
