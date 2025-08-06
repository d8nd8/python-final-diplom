from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from requests import get
from rest_framework import generics, status, filters as drf_filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    extend_schema_view,
)
from rest_framework.views import APIView
from yaml import safe_load

from .filters import ProductFilter
from .models import (
    EmailConfirmToken,
    Shop,
    Category,
    ProductInfo,
    Product,
    ProductParameter,
    Parameter,
    Cart,
    CartItem,
    Contact,
)
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PartnerUpdateSerializer,
    ProductSerializer,
    CartItemSerializer,
    ContactSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Для регистрации нового пользователя.
    """

    serializer_class = RegisterSerializer
    permission_classes = []

    @extend_schema(
        summary="Регистрация пользователя",
        responses={
            201: OpenApiResponse(RegisterSerializer),
            400: OpenApiResponse(
                description="Ошибка валидации данных", response=RegisterSerializer
            ),
        },
        tags=["Аутентификация"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = []

    @extend_schema(
        summary="Логин пользователя",
        responses={
            200: OpenApiResponse(LoginSerializer),
            400: OpenApiResponse(
                description="Ошибка валидации данных", response=LoginSerializer
            ),
        },
        tags=["Аутентификация"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ConfirmEmailView(APIView):
    permission_classes = []

    @extend_schema(
        summary="Подтверждение e-mail",
        parameters=[
            OpenApiParameter(
                name="token",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Токен подтверждения e-mail, полученный при регистрации",
            )
        ],
        responses={
            200: OpenApiResponse(description="E-mail успешно подтвержден"),
            400: OpenApiResponse(description="Неверный токен или ошибка валидации"),
        },
        tags=["Аутентификация"],
    )
    def get(self, request):
        token_key = request.query_params.get("token")
        token = get_object_or_404(EmailConfirmToken, token=token_key)
        if token.is_expired:
            return Response(
                {"detail": "Токен подтверждения истек."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = token.user
        user.is_active = True
        user.save()

        token.delete()
        return Response(
            {"detail": "E-mail успешно подтвержден."},
            status=status.HTTP_200_OK,
        )


class PartnerUpdateView(APIView):
    """
    Загрузка и обновление товаров магазина партнера.
    """

    parser_classes = [JSONParser]

    @extend_schema(
        summary="Обновление товаров магазинатам ",
        request=PartnerUpdateSerializer,
        responses={
            200: OpenApiResponse(description="Товары успешно обновлены"),
            400: OpenApiResponse(description="Ошибка валидации данных"),
            403: OpenApiResponse(
                description="Недостаточно прав для обновления товаров партнера"
            ),
        },
        tags=["Магазины / Партнеры"],
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse(
                {"detail": "Пользователь не авторизован."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if user.user_type != "shop":
            return JsonResponse(
                {"detail": "Недостаточно прав для обновления товаров партнера."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PartnerUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = request.data.get("url")
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError as e:
            return JsonResponse(
                {"detail": f"Неверный URL: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            yaml_file = get(url).content
            data = safe_load(yaml_file)
        except Exception as e:
            return JsonResponse(
                {"detail": f"Ошибка при загрузке YAML-файла: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shop, _ = Shop.objects.get_or_create(name=data["shop"], user=user)

        for cat in data.get("categories", []):
            category, _ = Category.objects.get_or_create(
                pk=cat["id"], defaults={"name": cat["name"]}
            )
            category.shops.add(shop)

        ProductInfo.objects.filter(shop=shop).delete()

        for item in data.get("goods", []):
            product, _ = Product.objects.get_or_create(
                name=item["name"], category_id=item["category"]
            )
            info = ProductInfo.objects.create(
                product=product,
                article=item["id"],
                model=item.get("model"),
                shop=shop,
                price=item["price"],
                price_rrc=item.get("price_rrc"),
                quantity=item["quantity"],
            )
            for pname, pvalue in item.get("parameters", {}).items():
                param, _ = Parameter.objects.get_or_create(name=pname)
                ProductParameter.objects.create(
                    product_info=info, parameter=param, value=pvalue
                )
        return JsonResponse(
            {"detail": "Товары успешно обновлены."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Получение списка товаров",
    responses={
        200: OpenApiResponse(
            response=ProductSerializer(many=True), description="Успешный список товаров"
        ),
    },
    tags=["Товары"],
)
class ProductListView(generics.ListAPIView):
    """
    Список товаров с фильтрами.
    """

    queryset = ProductInfo.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_class = ProductFilter
    search_fields = ["product__name", "product__description", "shop__name"]
    ordering_fields = ["price", "quantity", "product__name"]
    ordering = ["product__name"]


@extend_schema(
    summary="Корзина пользователя",
    responses={
        200: OpenApiResponse(
            response=CartItemSerializer(many=True),
            description="Успешное получение корзины",
        ),
        201: OpenApiResponse(description="Товар успешно добавлен в корзину"),
        204: OpenApiResponse(description="Товар успешно удален из корзины"),
    },
    tags=["Корзина"],
)
class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=["get"])
    def items(self, request):
        cart = self.get_cart()
        return Response(self.get_serializer(cart).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        cart = self.get_cart()
        serializer = CartItemSerializer
        serializer.is_valid(raise_exception=True)
        product_info = get_object_or_404(
            ProductInfo, pk=serializer.validated_data["product_info"].id
        )
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_info=product_info,
            defaults={"quantity": serializer.validated_data["quantity"]},
        )
        if not created:
            item.quantity += serializer.validated_data["quantity"]
            item.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def delete(self, request):
        cart = self.get_cart()
        item = get_object_or_404(CartItem, pk=request.data.get("item_id"), cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список контактов текущего пользователя",
        description="Возвращает все контакты, привязанные к авторизованному пользователю",
        tags=["Контакты"],
    ),
    retrieve=extend_schema(
        summary="Получить конкретный контакт",
        description="Детальная информация по одному контакту",
        tags=["Контакты"],
    ),
    create=extend_schema(
        summary="Создать контакт",
        description="Создание нового контакта для текущего пользователя",
        tags=["Контакты"],
    ),
    update=extend_schema(
        summary="Полное обновление контакта",
        description="Обновление всех полей контакта",
        tags=["Контакты"],
    ),
    partial_update=extend_schema(
        summary="Частичное обновление контакта",
        description="Обновление отдельных полей контакта",
        tags=["Контакты"],
    ),
    destroy=extend_schema(
        summary="Удалить контакт",
        description="Удаление контакта пользователя",
        tags=["Контакты"],
    ),
)
class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
