import os
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from requests import get
from rest_framework import generics, status, filters as drf_filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
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
    Order,
    OrderItem,
)
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PartnerUpdateSerializer,
    ProductSerializer,
    CartItemSerializer,
    ContactSerializer,
    ConfirmOrderSerializer,
    OrderSerializer,
    AvatarUploadSerializer,
    AvatarStatusSerializer,
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
        items = CartItem.objects.filter(cart=cart)
        return Response(self.get_serializer(items, many=True).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        cart = self.get_cart()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_info = get_object_or_404(
            ProductInfo, pk=serializer.validated_data["product_info"]
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

    @extend_schema(
        summary="Создать заказ из корзины",
        description="На основе содержимого корзины и указанного contact_id создаёт новый Order",
        tags=["Заказы"],
    )
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        cart = self.get_object()
        serializer = ConfirmOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = get_object_or_404(
            Contact,
            pk=serializer.validated_data["contact_id"],
            user=request.user,
        )
        order = Order.objects.create(
            user=request.user,
            contact=contact,
            status="pending",
        )
        for item in CartItem.objects.filter(cart=cart):
            OrderItem.objects.create(
                order=order,
                product=item.product_info,
                quantity=item.quantity,
            )

        CartItem.objects.filter(cart=cart).delete()

        return Response(OrderSerializer(order).data, status=201)


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


@extend_schema_view(
    list=extend_schema(
        summary="Получить список заказов текущего пользователя",
        description="Возвращает все заказы, сделанные авторизованным пользователем",
        tags=["Заказы"],
    ),
    retrieve=extend_schema(
        summary="Получить конкретный заказ",
        description="Детальная информация по одному заказу",
        tags=["Заказы"],
    ),
    create=extend_schema(
        summary="Создать заказ",
        description="Создание нового заказа на основе корзины пользователя",
        tags=["Заказы"],
    ),
    update=extend_schema(
        summary="Полное обновление заказа",
        description="Обновление всех полей заказа",
        tags=["Заказы"],
    ),
    partial_update=extend_schema(
        summary="Частичное обновление заказа",
        description="Обновление отдельных полей заказа",
        tags=["Заказы"],
    ),
    destroy=extend_schema(
        summary="Удалить заказ",
        description="Удаление заказа пользователя",
        tags=["Заказы"],
    ),
)
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Просмотр и подтверждение уже созданного заказа
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    @extend_schema(
        summary="Подтвердить заказ",
        description="Устанавливает статус `confirmed` и возвращает обновлённый заказ. Письмо с адресом доставки «мокается» и не уходит на SMTP.",
        tags=["Заказы"],
        request=ConfirmOrderSerializer,
        responses={200: OrderSerializer},
    )
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        order = self.get_object()

        if order.status == "confirmed":
            return Response(
                {"detail": "Заказ уже подтверждён."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ConfirmOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = get_object_or_404(
            Contact, pk=serializer.validated_data["contact_id"], user=request.user
        )

        order.status = "confirmed"
        order.contact = contact
        order.save()
        order.email_sent_log = (
            f"Письмо по заказу #{order.id} отправлено на {contact.email}"
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class SocialAuthView(APIView):
    """
    API для авторизации через социальные сети
    """
    permission_classes = []

    @extend_schema(
        summary="Получить доступные провайдеры OAuth2",
        description="Возвращает список доступных провайдеров для авторизации",
        tags=["OAuth2"],
        responses={
            200: OpenApiResponse(description="Список провайдеров"),
        },
    )
    def get(self, request):
        """Получить список доступных провайдеров"""
        providers = [
            {
                "name": "github",
                "auth_url": f"/social-auth/login/github/",
                "display_name": "GitHub"
            },
            {
                "name": "vk-oauth2", 
                "auth_url": f"/social-auth/login/vk-oauth2/",
                "display_name": "VK"
            }
        ]
        return Response(providers)


class SocialAuthCallbackView(APIView):
    """
    Обработка callback'а от OAuth2 провайдеров
    """
    permission_classes = []

    @extend_schema(
        summary="OAuth2 callback",
        description="Endpoint для обработки callback'а от OAuth2 провайдеров",
        tags=["OAuth2"],
        responses={
            200: OpenApiResponse(description="Успешная авторизация"),
            400: OpenApiResponse(description="Ошибка авторизации"),
        },
    )
    def get(self, request):
        """Обработка GET запроса от OAuth2 провайдера"""
        # Этот endpoint будет обрабатываться автоматически social_django
        # Здесь можно добавить дополнительную логику
        return Response({
            "message": "OAuth2 callback received",
            "status": "success"
        })


class SocialAuthStatusView(APIView):
    """
    Проверка статуса авторизации через соцсети
    """
    permission_classes = []

    @extend_schema(
        summary="Статус авторизации",
        description="Проверка статуса авторизации пользователя",
        tags=["OAuth2"],
        responses={
            200: OpenApiResponse(description="Статус авторизации"),
        },
    )
    def get(self, request):
        """Получить статус авторизации"""
        if request.user.is_authenticated:
            # Получаем связанные соцсети
            from social_django.models import UserSocialAuth
            social_accounts = UserSocialAuth.objects.filter(user=request.user)
            
            providers = []
            for account in social_accounts:
                providers.append({
                    "provider": account.provider,
                    "uid": account.uid,
                    "extra_data": account.extra_data
                })
            
            return Response({
                "authenticated": True,
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email
                },
                "social_accounts": providers
            })
        else:
            return Response({
                "authenticated": False,
                "message": "User not authenticated"
            })


class AvatarUploadView(APIView):
    """
    API для загрузки аватарки пользователя
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Загрузить аватарку",
        description="Асинхронная загрузка и обработка аватарки пользователя через Celery",
        tags=["Профиль"],
        request=AvatarUploadSerializer,
        responses={
            202: OpenApiResponse(description="Аватарка принята в обработку"),
            400: OpenApiResponse(description="Ошибка валидации"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    )
    def post(self, request):
        """Загрузить аватарку пользователя"""
        serializer = AvatarUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Сохраняем временный файл
                avatar_file = request.FILES['avatar']
                temp_path = os.path.join(settings.MEDIA_ROOT, 'avatars', 'temp', f"temp_{request.user.id}_{avatar_file.name}")
                
                # Создаем папку если не существует
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
                with open(temp_path, 'wb+') as destination:
                    for chunk in avatar_file.chunks():
                        destination.write(chunk)
                
                # Запускаем асинхронную обработку через Celery
                from .tasks.avatar_tasks import process_avatar, cleanup_old_avatars
                
                # Сначала очищаем старые аватарки
                cleanup_task = cleanup_old_avatars.delay(request.user.id)
                
                # Затем обрабатываем новую
                process_task = process_avatar.delay(request.user.id, temp_path)
                
                return Response({
                    'message': 'Аватарка принята в обработку',
                    'task_id': process_task.id,
                    'cleanup_task_id': cleanup_task.id,
                    'status': 'processing'
                }, status=status.HTTP_202_ACCEPTED)
                
            except Exception as e:
                return Response({
                    'error': f'Ошибка при загрузке: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarStatusView(APIView):
    """
    API для проверки статуса обработки аватарки
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Статус обработки аватарки",
        description="Проверка статуса асинхронной обработки аватарки",
        tags=["Профиль"],
        parameters=[
            OpenApiParameter(
                name="task_id",
                type=str,
                location=OpenApiParameter.QUERY,
                description="ID задачи Celery",
                required=True
            ),
        ],
        responses={
            200: AvatarStatusSerializer,
            400: OpenApiResponse(description="Не указан task_id"),
            401: OpenApiResponse(description="Не авторизован"),
        },
    )
    def get(self, request):
        """Получить статус обработки аватарки"""
        task_id = request.query_params.get('task_id')
        
        if not task_id:
            return Response({
                'error': 'Не указан task_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from celery.result import AsyncResult
            
            # Получаем результат задачи
            task_result = AsyncResult(task_id)
            
            if task_result.ready():
                if task_result.successful():
                    result = task_result.result
                    return Response({
                        'task_id': task_id,
                        'status': 'completed',
                        'message': result.get('message', 'Обработка завершена'),
                        'progress': 100
                    })
                else:
                    return Response({
                        'task_id': task_id,
                        'status': 'failed',
                        'message': 'Ошибка при обработке',
                        'progress': 0
                    })
            else:
                # Задача еще выполняется
                return Response({
                    'task_id': task_id,
                    'status': 'processing',
                    'message': 'Аватарка обрабатывается',
                    'progress': 50  # Примерный прогресс
                })
                
        except Exception as e:
            return Response({
                'error': f'Ошибка при получении статуса: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
