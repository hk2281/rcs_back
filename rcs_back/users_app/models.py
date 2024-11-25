from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from rcs_back.containers_app.models import Building


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with required email and no username"""
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    username = None
    first_name = None
    last_name = None

    email = models.EmailField(
        unique=True,
        verbose_name="почта"
    )

    building = models.ManyToManyField(
        to=Building,
        verbose_name="здания",
        blank=True
    )

    name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="ФИО"
    )

    phone = models.CharField(
        max_length=16,
        blank=True,
        verbose_name="номер телефона"
    )

    objects = UserManager()


class MJMLTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, verbose_name="Template Name")
    mjml_content = models.TextField(verbose_name="MJML Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "MJML Template"
        verbose_name_plural = "MJML Templates"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name