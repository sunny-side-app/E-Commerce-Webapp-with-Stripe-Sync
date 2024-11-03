from django.db import models


class Size(models.Model):
    name = models.CharField(max_length=10, unique=True)  # S, M, L, XLなど
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=50, unique=True)  # メンズ、レディース、キッズなど
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClothesType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # シャツ、ズボン、ジャケットなど
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)  # CHANEL、NIKEなど
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
