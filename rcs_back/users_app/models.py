from secrets import choice
from string import ascii_letters, digits
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

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
    email = models.EmailField(unique=True, verbose_name="почта")
    building = models.ForeignKey(
        to=Building,
        on_delete=models.PROTECT,
        verbose_name="здание",
        blank=True,
        null=True
    )

    objects = UserManager()


class RegistrationToken(models.Model):
    """Модель токена для регистрации"""

    TOKEN_LENGTH = 32
    EXPIRATION_DAYS = 7

    token = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="токен"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="время генерации"
    )

    is_claimed = models.BooleanField(
        default=False,
        verbose_name="использован"
    )

    def generate_token(self) -> str:
        """Генерирует рандомный токен"""
        token = ''.join(choice(
            ascii_letters + digits
        ) for _ in range(self.TOKEN_LENGTH))
        return token

    def set_token(self) -> None:
        """Задать значение поля token"""
        while True:
            token = self.generate_token()
            """Проверка на уникальность"""
            if not RegistrationToken.objects.filter(
                token=token
            ).first():
                break
        self.token = token

    def has_expired(self) -> bool:
        """Исткекло ли время действия токена?"""
        today = timezone.now().day
        return today - self.created_at.day > self.EXPIRATION_DAYS

    def __str__(self) -> str:
        return f"токен №{self.pk}"

    class Meta:
        verbose_name = "токен для регистрации"
        verbose_name_plural = "токены для регистрации"
