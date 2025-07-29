import secrets

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

USER_TYPE_CHOICES = (
    ("shop", "Магазин"),
    ("buyer", "Покупатель"),
    ("admin", "Администратор"),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        if not email:
            raise ValueError("Пользователь должен иметь адрес электронной почты")
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Неверный формат адреса электронной почты")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = "email"
    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(verbose_name="Компания", max_length=40, blank=True)
    position = models.CharField(verbose_name="Должность", max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    type = models.CharField(
        verbose_name="Тип пользователя",
        choices=USER_TYPE_CHOICES,
        max_length=5,
        default="buyer",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"
        ordering = ("email",)


class Shop(models.Model):
    """Модель магазина"""

    name = models.CharField(max_length=255, unique=True)
    url = models.TextField(blank=True, null=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="shop", verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категории товаров"""

    shops = models.ManyToManyField(
        Shop, related_name="categories", verbose_name="Магазины"
    )
    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название категории"
    )


class Product(models.Model):
    """Модель товара"""

    name = models.CharField(max_length=255, verbose_name="Название товара")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категория",
    )


class ProductInfo(models.Model):
    """Модель информации о товаре"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="info", verbose_name="Товар"
    )
    article = models.CharField(max_length=255, unique=True, verbose_name="Артикул")
    model = models.CharField(
        max_length=255, verbose_name="Модель", blank=True, null=True
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="product_info",
        verbose_name="Магазин",
    )
    name = models.CharField(max_length=255, verbose_name="Название товара")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price_rrc = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена RRC", blank=True, null=True
    )


class Parameter(models.Model):
    """Модель параметра товара"""

    name = models.CharField(max_length=255, verbose_name="Название параметра")


class ProductParameter(models.Model):
    """Модель параметра товара"""

    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="parameters",
        verbose_name="Информация о товаре",
    )
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name="product_parameters",
        verbose_name="Параметр",
    )
    value = models.CharField(max_length=255, verbose_name="Значение параметра")

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(
                fields=["product_info", "parameter"], name="unique_product_parameter"
            ),
        ]


class Order(models.Model):
    """Модель заказа"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, related_name="orders", verbose_name="Магазин"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(
        max_length=20, default="pending", verbose_name="Статус заказа"
    )
    contact = models.ForeignKey(
        "Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.email} at {self.shop.name}"


class OrderItem(models.Model):
    """Модель элемента заказа"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ"
    )
    product = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Товар",
    )
    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Магазин",
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self):
        return f"Item {self.id} in Order {self.order.id}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
        constraints = [
            models.UniqueConstraint(
                fields=["order_id", "product_info"], name="unique_order_item"
            ),
        ]


class Contact(models.Model):
    """Модель контакта"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Пользователь",
    )
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    street = models.CharField(
        max_length=255, verbose_name="Улица", blank=True, null=True
    )
    house = models.CharField(max_length=10, verbose_name="Дом", blank=True, null=True)
    building = models.CharField(
        max_length=10, verbose_name="Корпус", blank=True, null=True
    )
    apartment = models.CharField(
        max_length=10, verbose_name="Квартира", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )
    type = models.CharField(
        max_length=20,
        choices=[("email", "Email"), ("phone", "Phone")],
        verbose_name="Тип контакта",
    )
    value = models.CharField(max_length=255, verbose_name="Значение контакта")

    def __str__(self):
        return self.type


class EmailConfirmToken(models.Model):
    """Модель токена подтверждения электронной почты"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_tokens",
        verbose_name="Пользователь",
    )
    token = models.CharField(max_length=64, unique=True, verbose_name="Токен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    expires_at = models.DateTimeField(verbose_name="Дата истечения срока действия")

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()

    def __str__(self):
        return f"Token for {self.user.email}"
