import django_filters
from .models import ProductInfo


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="product__name", lookup_expr="icontains", label="Название товара"
    )
    category = django_filters.CharFilter(
        field_name="product__category__name", lookup_expr="icontains", label="Категория"
    )
    supplier = django_filters.CharFilter(
        field_name="shop__name", lookup_expr="icontains", label="Поставщик"
    )
    price_min = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Минимальная цена"
    )
    price_max = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Максимальная цена"
    )
    quantity_min = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="gte", label="Мин. количество"
    )
    quantity_max = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="lte", label="Макс. количество"
    )

    class Meta:
        model = ProductInfo
        # explicit empty fields to avoid auto-generation
        fields = []
