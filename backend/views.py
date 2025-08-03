from rest_framework import generics, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import RegisterSerializer, LoginSerializer


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
        tags=["Authentication"],
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
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
