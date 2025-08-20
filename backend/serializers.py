from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import (
    User,
    EmailConfirmToken,
    ProductParameter,
    ProductInfo,
    Contact,
    OrderItem,
    Order,
)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "token",
        )

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Пароли не совпадают.")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        EmailConfirmToken.objects.create(user=user)
        return user

    def get_token(self, user):
        token_obj = (
            EmailConfirmToken.objects.filter(user=user).order_by("-created_at").first()
        )
        return token_obj.token if token_obj else None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Неверный email или пароль.")
        if not user.is_active:
            raise serializers.ValidationError("Профиль пользователя не подтвержден.")
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class PartnerUpdateSerializer(serializers.Serializer):
    url = serializers.URLField(help_text="Прямая ссылка на YAML-файл прайса")


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.CharField(source="parameter.name")

    class Meta:
        model = ProductParameter
        fields = ["parameter", "value"]


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(source="product.name")
    category = serializers.CharField(source="product.category.name")
    characteristics = ProductParameterSerializer(source="parameters", many=True)
    quantity = serializers.IntegerField()
    supplier = serializers.CharField(source="shop.name")
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )

    class Meta:
        model = ProductInfo
        fields = [
            "article",
            "name",
            "model",
            "category",
            "supplier",
            "characteristics",
            "price",
            "price_rrc",
            "quantity",
        ]


class CartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(source="product_info.product.name", read_only=True)
    shop = serializers.CharField(source="product_info.shop.name", read_only=True)
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(
        source="product_info.price", max_digits=10, decimal_places=2, read_only=True
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "name", "shop", "quantity", "price", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantity * obj.product_info.price


class AddressSerializer(serializers.Serializer):
    city = serializers.CharField(required=False, allow_null=True, max_length=100)
    street = serializers.CharField(required=False, allow_null=True, max_length=255)
    house = serializers.CharField(required=False, allow_null=True, max_length=10)
    building = serializers.CharField(required=False, allow_null=True, max_length=10)
    structure = serializers.CharField(required=False, allow_null=True, max_length=10)
    apartment = serializers.CharField(required=False, allow_null=True, max_length=10)


class ContactSerializer(serializers.Serializer):
    address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        fields = [
            "id",
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "phone",
            "address",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        address_data = validated_data.pop("address", None)
        user = self.context["request"].user
        return Contact.objects.create(
            user=user,
            **validated_data,
            **address_data,
        )

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        for attr, value in address_data.items():
            setattr(instance.address, attr, value)
        instance.save()
        return instance


class ConfirmOrderSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField()


class OrderItemSerializer(serializers.Serializer):
    product = serializers.CharField(source="product.name", read_only=True)
    quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True, read_only=True)
    contact = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "items", "contact"]


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField(
        max_length=None,
        allow_empty_file=False,
        use_url=False,
        help_text="Загрузите изображение для профиля (JPG, PNG, GIF)",
    )

    def validate_avatar(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Размер файла не должен превышать 5MB")

        allowed_formats = ["image/jpeg", "image/png", "image/gif"]
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError(
                "Поддерживаются только форматы JPG, PNG и GIF"
            )

        return value


class AvatarStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField(help_text="ID задачи Celery")
    status = serializers.CharField(help_text="Статус обработки")
    message = serializers.CharField(help_text="Сообщение о статусе")
    progress = serializers.IntegerField(help_text="Прогресс обработки (0-100)")
