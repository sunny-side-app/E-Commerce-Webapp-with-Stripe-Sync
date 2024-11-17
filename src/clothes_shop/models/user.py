from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, name, password, role, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not name:
            raise ValueError("Name is required")
        if not password:
            raise ValueError("Password is required")
        if not role or (role != "admin" and role != "customer"):
            raise ValueError("role is required ('admin' or 'customer')")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password)


class User(AbstractBaseUser, PermissionsMixin):
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True, null=True)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=128, null=True)
    role = models.CharField(
        max_length=50,
        choices=[("guest", "Guest"), ("customer", "Customer"), ("admin", "Admin")],
        default="guest",
    )  # 次善の策としてmodelのrole項目をデフォルトでguest
    email_validated_at = models.DateTimeField(null=True, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(
        default=timezone.now
    )  # Djangoのデフォルトユーザーモデル(AbstractUser,AbstractBaseUser)で、ユーザーのログイン履歴やアカウント作成日を管理するためにmust
    last_login = models.DateTimeField(
        null=True, blank=True
    )  # Djangoのデフォルトユーザーモデル(AbstractUser,AbstractBaseUser)で、ユーザーのログイン履歴やアカウント作成日を管理するためにmust
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
