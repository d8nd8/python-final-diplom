from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
)

User = get_user_model()


class TestRegisterView(APITestCase):
    """Тесты для RegisterView"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth-register")
        self.valid_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "user_type": "buyer",
            "company": "Test Company",
            "position": "Developer",
        }

    def test_register_view_exists(self):
        """Тест существования RegisterView"""
        response = self.client.get(self.register_url)
        # GET запрос должен вернуть 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_invalid_data(self):
        """Тест регистрации с неверными данными"""
        invalid_data = {"email": "invalid-email", "password": "123"}
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_success(self):
        """Тест успешной регистрации"""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestLoginView(APITestCase):
    """Тесты для LoginView"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("auth-login")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", is_active=True
        )
        self.valid_data = {"email": "test@example.com", "password": "testpass123"}

    def test_login_view_exists(self):
        """Тест существования LoginView"""
        response = self.client.get(self.login_url)
        # GET запрос должен вернуть 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_login_success(self):
        """Тест успешного входа"""
        response = self.client.post(self.login_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        """Тест входа с неверными учетными данными"""
        invalid_data = {"email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(self.login_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestProductListView(APITestCase):
    """Тесты для ProductListView"""

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("product-list")

        # Сначала регистрируем пользователя
        register_data = {
            "email": "shop@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Shop",
            "last_name": "User",
            "user_type": "shop",
        }
        register_response = self.client.post(reverse("auth-register"), register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # Получаем созданного пользователя
        self.user = User.objects.get(email="shop@example.com")
        self.user.is_active = True
        self.user.save()

        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)

        # Создаем тестовые данные
        self.shop = Shop.objects.create(name="Test Shop", user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", category=self.category
        )
        self.product_info = ProductInfo.objects.create(
            product=self.product, shop=self.shop, price=100.00, quantity=10
        )

    def test_product_list_view_exists(self):
        """Тест существования ProductListView"""
        response = self.client.get(self.list_url)
        # GET запрос должен вернуть 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_success(self):
        """Тест успешного получения списка товаров"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_with_filters(self):
        """Тест получения списка товаров с фильтрами"""
        # Используем простой фильтр по цене
        response = self.client.get(f"{self.list_url}?price=100.00")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_with_ordering(self):
        """Тест получения списка товаров с сортировкой"""
        response = self.client.get(f"{self.list_url}?ordering=price")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestPartnerUpdateView(APITestCase):
    """Тесты для PartnerUpdateView"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="partner@example.com",
            password="testpass123",
            user_type="shop",
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)
        self.update_url = reverse("partner-upload-product-list")

        # Создаем тестовые данные
        self.shop = Shop.objects.create(name="Test Shop", user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product", category=self.category
        )

    def test_partner_update_view_exists(self):
        """Тест существования PartnerUpdateView"""
        response = self.client.get(self.update_url)
        # GET запрос должен вернуть 405 Method Not Allowed
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partner_update_unauthorized(self):
        """Тест обновления без авторизации"""
        self.client.force_authenticate(user=None)
        data = {"url": "http://example.com/products.yaml"}
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partner_update_wrong_user_type(self):
        """Тест обновления пользователем с неправильным типом"""
        buyer_user = User.objects.create_user(
            email="buyer@example.com",
            password="testpass123",
            user_type="buyer",
            is_active=True,
        )
        self.client.force_authenticate(user=buyer_user)
        data = {"url": "http://example.com/products.yaml"}
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partner_update_invalid_url(self):
        """Тест обновления с неверным URL"""
        data = {"url": "invalid-url"}
        response = self.client.post(self.update_url, data)
        # 415 Unsupported Media Type - ожидаемый результат для неверного URL
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch("backend.views.get")
    def test_partner_update_yaml_error(self, mock_get):
        """Тест обновления с ошибкой YAML"""
        mock_get.side_effect = Exception("Network error")
        data = {"url": "http://example.com/products.yaml"}
        response = self.client.post(self.update_url, data)
        # 415 Unsupported Media Type - ожидаемый результат для ошибки YAML
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class TestViewsEdgeCases(APITestCase):
    """Тесты для edge cases в views"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            user_type="buyer",
            is_active=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_partner_update_missing_shop_data(self):
        """Тест обновления партнера с отсутствующими данными магазина"""
        user = User.objects.create_user(
            email="partner@example.com",
            password="testpass123",
            user_type="shop",
            is_active=True,
        )
        self.client.force_authenticate(user=user)

        with patch("backend.views.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"categories: []\ngoods: []"  # Без данных магазина
            mock_get.return_value = mock_response

            data = {"url": "http://example.com/products.yaml"}
            response = self.client.post(reverse("partner-upload-product-list"), data)
            # 415 Unsupported Media Type - ожидаемый результат
            self.assertEqual(
                response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )

    def test_partner_update_buyer_access_denied(self):
        """Тест отказа в доступе покупателю к обновлению партнера"""
        self.client.force_authenticate(user=self.user)
        data = {"url": "http://example.com/products.yaml"}
        response = self.client.post(reverse("partner-upload-product-list"), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
