from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, EmailConfirmToken, ProductParameter, ProductInfo


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
