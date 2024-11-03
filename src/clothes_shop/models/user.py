from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email_address = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    email_validated_at = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
