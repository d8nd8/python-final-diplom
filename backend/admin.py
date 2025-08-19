from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Count
from django.conf import settings

from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import RangeDateFilter, RelatedDropdownFilter, ChoicesDropdownFilter, RangeNumericFilter
from unfold.decorators import display
from import_export.admin import ImportExportModelAdmin

from .models import (
    User, Shop, Category, Product, ProductInfo, Parameter, 
    ProductParameter, Order, OrderItem, Cart, CartItem, Contact, EmailConfirmToken
)


class ShopInline(TabularInline):
    model = Shop
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('name', 'url', 'created_at')


class ContactInline(TabularInline):
    model = Contact
    extra = 0
    fields = ('last_name', 'first_name', 'patronymic', 'email', 'phone', 'city')


@admin.register(User)
class UserAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = (
        'formatted_email',
        'full_name',
        'user_type_badge',
        'company',
        'position',
        'is_active_badge',
        'date_joined',
    )
    list_filter = (
        ('user_type', ChoicesDropdownFilter),
        ('is_active', ChoicesDropdownFilter),
        ('date_joined', RangeDateFilter),
        ('is_staff', ChoicesDropdownFilter),
        ('is_superuser', ChoicesDropdownFilter),
    )
    search_fields = ('email', 'first_name', 'last_name', 'company')
    readonly_fields = ('date_joined', 'last_login')
    list_per_page = 25
    ordering = ('-date_joined',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("email", "username"),
                ("first_name", "last_name"),
                ("company", "position"),
                "user_type",
            ],
        }),
        (_("Права доступа"), {
            "classes": ["tab"],
            "fields": [
                ("is_active", "is_staff"),
                ("is_superuser", "groups"),
                "user_permissions",
            ],
        }),
        (_("Важные даты"), {
            "classes": ["tab"],
            "fields": [
                ("date_joined", "last_login"),
            ],
        }),
    )
    
    inlines = [ShopInline, ContactInline]
    
    @display(
        description=_("Email"),
        ordering="email",
    )
    def formatted_email(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.email
        )
    
    @display(
        description=_("Полное имя"),
        ordering="first_name",
    )
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name and obj.last_name else "-"
    
    @display(
        description=_("Тип пользователя"),
        ordering="user_type",
        label={
            "shop": "primary",
            "buyer": "secondary",
            "admin": "danger",
        },
    )
    def user_type_badge(self, obj):
        return obj.user_type, obj.get_user_type_display()
    
    @display(
        description=_("Активен"),
        ordering="is_active",
        label={
            True: "success",
            False: "danger",
        },
    )
    def is_active_badge(self, obj):
        return obj.is_active, "Активен" if obj.is_active else "Неактивен"
    
    @display(
        description=_("Дата регистрации"),
        ordering="date_joined",
    )
    def date_joined(self, obj):
        return obj.date_joined.strftime("%d.%m.%Y %H:%M") if obj.date_joined else "-"


@admin.register(Shop)
class ShopAdmin(ModelAdmin):
    list_display = (
        'formatted_name',
        'user_link',
        'url_link',
        'products_count',
        'orders_count',
        'created_at',
    )
    list_filter = (
        ('created_at', RangeDateFilter),
        ('updated_at', RangeDateFilter),
    )
    search_fields = ('name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "name",
                "url",
                "user",
            ],
        }),
        (_("Дополнительно"), {
            "classes": ["tab"],
            "fields": [
                ("created_at", "updated_at"),
            ],
        }),
    )
    
    @display(
        description=_("Название"),
        ordering="name",
    )
    def formatted_name(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.name
        )
    
    @display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:backend_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.user.email
            )
        return "-"
    
    @display(
        description=_("URL"),
    )
    def url_link(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" class="text-blue-600 hover:text-blue-800">{}</a>',
                obj.url, obj.url
            )
        return "-"
    
    @display(
        description=_("Товары"),
        ordering="product_info__count",
    )
    def products_count(self, obj):
        count = obj.product_info.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )
    
    @display(
        description=_("Заказы"),
        ordering="orders__count",
    )
    def orders_count(self, obj):
        count = obj.orders.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = (
        'formatted_name',
        'shops_count',
        'products_count',
    )
    search_fields = ('name',)
    list_per_page = 25
    ordering = ('name',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "name",
                "shops",
            ],
        }),
    )
    
    @display(
        description=_("Название"),
        ordering="name",
    )
    def formatted_name(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.name
        )
    
    @display(
        description=_("Магазины"),
        ordering="shops__count",
    )
    def shops_count(self, obj):
        count = obj.shops.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )
    
    @display(
        description=_("Товары"),
        ordering="products__count",
    )
    def products_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )


class ProductParameterInline(TabularInline):
    model = ProductParameter
    extra = 1
    fields = ('parameter', 'value')


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        'formatted_name',
        'category_link',
        'shops_count',
        'parameters_count',
    )
    list_filter = (
        ('category', RelatedDropdownFilter),
    )
    search_fields = ('name', 'category__name')
    list_per_page = 25
    ordering = ('name',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "name",
                "category",
            ],
        }),
    )
    

    
    @display(
        description=_("Название"),
        ordering="name",
    )
    def formatted_name(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.name
        )
    
    @display(
        description=_("Категория"),
        ordering="category__name",
    )
    def category_link(self, obj):
        if obj.category:
            url = reverse('admin:backend_category_change', args=[obj.category.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.category.name
            )
        return "-"
    
    @display(
        description=_("Магазины"),
        ordering="info__shop__count",
    )
    def shops_count(self, obj):
        count = obj.info.values('shop').distinct().count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )
    
    @display(
        description=_("Параметры"),
        ordering="info__parameters__count",
    )
    def parameters_count(self, obj):
        count = obj.info.aggregate(
            param_count=Count('parameters')
        )['param_count'] or 0
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )


@admin.register(ProductInfo)
class ProductInfoAdmin(ModelAdmin):
    inlines = [ProductParameterInline]
    list_display = (
        'formatted_article',
        'product_link',
        'shop_link',
        'formatted_price',
        'formatted_price_rrc',
        'quantity',
        'model',
    )
    list_filter = (
        ('shop', RelatedDropdownFilter),
        ('product__category', RelatedDropdownFilter),
        ('price', RangeNumericFilter),
        ('quantity', ChoicesDropdownFilter),
    )
    search_fields = ('article', 'model', 'product__name', 'shop__name')
    list_per_page = 25
    ordering = ('-price',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("product", "shop"),
                ("article", "model"),
                ("price", "price_rrc"),
                "quantity",
            ],
        }),
    )
    
    @display(
        description=_("Артикул"),
        ordering="article",
    )
    def formatted_article(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.article
        )
    
    @display(
        description=_("Товар"),
        ordering="product__name",
    )
    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:backend_product_change', args=[obj.product.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.product.name
            )
        return "-"
    
    @display(
        description=_("Магазин"),
        ordering="shop__name",
    )
    def shop_link(self, obj):
        if obj.shop:
            url = reverse('admin:backend_shop_change', args=[obj.shop.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.shop.name
            )
        return "-"
    
    @display(
        description=_("Цена"),
        ordering="price",
    )
    def formatted_price(self, obj):
        if obj.price:
            return format_html(
                '<span class="font-semibold text-green-600">{} ₽</span>',
                f"{obj.price:.2f}"
            )
        return "-"
    
    @display(
        description=_("Цена RRC"),
        ordering="price_rrc",
    )
    def formatted_price_rrc(self, obj):
        if obj.price_rrc:
            return format_html(
                '<span class="font-medium text-blue-600">{} ₽</span>',
                f"{obj.price_rrc:.2f}"
            )
        return "-"


@admin.register(Parameter)
class ParameterAdmin(ModelAdmin):
    list_display = (
        'formatted_name',
        'products_count',
    )
    search_fields = ('name',)
    list_per_page = 25
    ordering = ('name',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "name",
            ],
        }),
    )
    
    @display(
        description=_("Название"),
        ordering="name",
    )
    def formatted_name(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            obj.name
        )
    
    @display(
        description=_("Товары"),
        ordering="product_parameters__count",
    )
    def products_count(self, obj):
        count = obj.product_parameters.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )


@admin.register(ProductParameter)
class ProductParameterAdmin(ModelAdmin):
    list_display = (
        'product_info_link',
        'parameter_link',
        'value',
    )
    list_filter = (
        ('parameter', RelatedDropdownFilter),
        ('product_info__shop', RelatedDropdownFilter),
    )
    search_fields = ('value', 'parameter__name', 'product_info__product__name')
    list_per_page = 25
    ordering = ('parameter__name',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("product_info", "parameter"),
                "value",
            ],
        }),
    )
    
    @display(
        description=_("Информация о товаре"),
        ordering="product_info__product__name",
    )
    def product_info_link(self, obj):
        if obj.product_info:
            url = reverse('admin:backend_productinfo_change', args=[obj.product_info.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, f"{obj.product_info.product.name} @ {obj.product_info.shop.name}"
            )
        return "-"
    
    @display(
        description=_("Параметр"),
        ordering="parameter__name",
    )
    def parameter_link(self, obj):
        if obj.parameter:
            url = reverse('admin:backend_parameter_change', args=[obj.parameter.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.parameter.name
            )
        return "-"


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'shop', 'quantity')
    fields = ('product', 'shop', 'quantity')
    can_delete = False


@admin.register(Order)
class OrderAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = (
        'formatted_id',
        'user_link',
        'shop_link',
        'status_badge',
        'items_count',
        'total_amount',
        'contact_link',
        'created_at',
    )
    list_filter = (
        ('status', ChoicesDropdownFilter),
        ('shop', RelatedDropdownFilter),
        ('created_at', RangeDateFilter),
        ('updated_at', RangeDateFilter),
    )
    search_fields = ('id', 'user__email', 'shop__name', 'contact__last_name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("user", "shop"),
                ("status", "contact"),
            ],
        }),
        (_("Дополнительно"), {
            "classes": ["tab"],
            "fields": [
                ("created_at", "updated_at"),
            ],
        }),
    )
    
    inlines = [OrderItemInline]
    
    @display(
        description=_("ID"),
        ordering="id",
    )
    def formatted_id(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">#{}</span>',
            obj.id
        )
    
    @display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:backend_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.user.email
            )
        return "-"
    
    @display(
        description=_("Магазин"),
        ordering="shop__name",
    )
    def shop_link(self, obj):
        if obj.shop:
            url = reverse('admin:backend_shop_change', args=[obj.shop.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.shop.name
            )
        return "-"
    
    @display(
        description=_("Статус"),
        ordering="status",
        label={
            "pending": "secondary",
            "confirmed": "info",
            "shipped": "warning",
            "delivered": "success",
            "cancelled": "danger",
        },
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()
    
    @display(
        description=_("Позиции"),
        ordering="items__count",
    )
    def items_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )
    
    @display(
        description=_("Сумма"),
        ordering="items__quantity",
    )
    def total_amount(self, obj):
        total = sum(item.product.price * item.quantity for item in obj.items.all())
        return format_html(
            '<span class="font-semibold text-green-600">{} ₽</span>',
            f"{total:.2f}"
        )
    
    @display(
        description=_("Контакт"),
        ordering="contact__last_name",
    )
    def contact_link(self, obj):
        if obj.contact:
            url = reverse('admin:backend_contact_change', args=[obj.contact.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, f"{obj.contact.last_name} {obj.contact.first_name}"
            )
        return "-"


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = (
        'formatted_id',
        'order_link',
        'product_link',
        'shop_link',
        'quantity',
        'item_price',
        'total_price',
    )
    list_filter = (
        ('order__shop', RelatedDropdownFilter),
        ('order__status', ChoicesDropdownFilter),
        ('quantity', ChoicesDropdownFilter),
    )
    search_fields = ('id', 'order__id', 'product__product__name')
    list_per_page = 25
    ordering = ('-order__created_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("order", "product"),
                ("shop", "quantity"),
            ],
        }),
    )
    
    @display(
        description=_("ID"),
        ordering="id",
    )
    def formatted_id(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">#{}</span>',
            obj.id
        )
    
    @display(
        description=_("Заказ"),
        ordering="order__id",
    )
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:backend_order_change', args=[obj.order.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">#{}</a>',
                url, obj.order.id
            )
        return "-"
    
    @display(
        description=_("Товар"),
        ordering="product__product__name",
    )
    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:backend_productinfo_change', args=[obj.product.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.product.product.name
            )
        return "-"
    
    @display(
        description=_("Магазин"),
        ordering="shop__name",
    )
    def shop_link(self, obj):
        if obj.shop:
            url = reverse('admin:backend_shop_change', args=[obj.shop.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.shop.name
            )
        return "-"
    
    @display(
        description=_("Цена за единицу"),
        ordering="product__price",
    )
    def item_price(self, obj):
        if obj.product:
            return format_html(
                '<span class="font-medium text-gray-700">{} ₽</span>',
                f"{obj.product.price:.2f}"
            )
        return "-"
    
    @display(
        description=_("Общая стоимость"),
        ordering="product__price",
    )
    def total_price(self, obj):
        if obj.product:
            total = obj.product.price * obj.quantity
            return format_html(
                '<span class="font-semibold text-green-600">{} ₽</span>',
                f"{total:.2f}"
            )
        return "-"


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = (
        'formatted_id',
        'user_link',
        'items_count',
        'total_amount',
        'updated_at',
    )
    list_filter = (
        ('updated_at', RangeDateFilter),
    )
    search_fields = ('id', 'user__email')
    readonly_fields = ('updated_at',)
    list_per_page = 25
    ordering = ('-updated_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "user",
            ],
        }),
        (_("Дополнительно"), {
            "classes": ["tab"],
            "fields": [
                "updated_at",
            ],
        }),
    )
    
    @display(
        description=_("ID"),
        ordering="id",
    )
    def formatted_id(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">#{}</span>',
            obj.id
        )
    
    @display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:backend_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.user.email
            )
        return "-"
    
    @display(
        description=_("Позиции"),
        ordering="items__count",
    )
    def items_count(self, obj):
        count = obj.items.count()
        return format_html(
            '<span class="font-medium text-gray-700">{}</span>',
            count
        )
    
    @display(
        description=_("Сумма"),
        ordering="items__quantity",
    )
    def total_amount(self, obj):
        total = sum(item.product_info.price * item.quantity for item in obj.items.all())
        return format_html(
            '<span class="font-semibold text-green-600">{} ₽</span>',
            f"{total:.2f}"
        )


@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = (
        'formatted_id',
        'cart_link',
        'product_link',
        'quantity',
        'item_price',
        'total_price',
    )
    list_filter = (
        ('quantity', ChoicesDropdownFilter),
    )
    search_fields = ('id', 'cart__user__email', 'product_info__product__name')
    list_per_page = 25
    ordering = ('-cart__updated_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                ("cart", "product_info"),
                "quantity",
            ],
        }),
    )
    
    @display(
        description=_("ID"),
        ordering="id",
    )
    def formatted_id(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">#{}</span>',
            obj.id
        )
    
    @display(
        description=_("Корзина"),
        ordering="cart__id",
    )
    def cart_link(self, obj):
        if obj.cart:
            url = reverse('admin:backend_cart_change', args=[obj.cart.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">#{}</a>',
                url, obj.cart.id
            )
        return "-"
    
    @display(
        description=_("Товар"),
        ordering="product_info__product__name",
    )
    def product_link(self, obj):
        if obj.product_info:
            url = reverse('admin:backend_productinfo_change', args=[obj.product_info.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.product_info.product.name
            )
        return "-"
    
    @display(
        description=_("Цена за единицу"),
        ordering="product_info__price",
    )
    def item_price(self, obj):
        if obj.product_info:
            return format_html(
                '<span class="font-medium text-gray-700">{} ₽</span>',
                f"{obj.product_info.price:.2f}"
            )
        return "-"
    
    @display(
        description=_("Общая стоимость"),
        ordering="product_info__price",
    )
    def total_price(self, obj):
        if obj.product_info:
            total = obj.product_info.price * obj.quantity
            return format_html(
                '<span class="font-semibold text-green-600">{} ₽</span>',
                f"{total:.2f}"
            )
        return "-"


@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = (
        'formatted_name',
        'user_link',
        'email',
        'phone',
        'city',
        'full_address',
    )
    list_filter = (
        ('city', ChoicesDropdownFilter),
    )
    search_fields = ('last_name', 'first_name', 'patronymic', 'email', 'phone', 'city')
    list_per_page = 25
    ordering = ('last_name', 'first_name')
    
    fieldsets = (
        (_("Личная информация"), {
            "fields": [
                ("last_name", "first_name"),
                "patronymic",
                ("email", "phone"),
            ],
        }),
        (_("Адрес"), {
            "classes": ["tab"],
            "fields": [
                "city",
                "street",
                ("house", "building"),
                ("structure", "apartment"),
            ],
        }),
        (_("Связь"), {
            "classes": ["tab"],
            "fields": [
                "user",
            ],
        }),
    )
    
    @display(
        description=_("ФИО"),
        ordering="last_name",
    )
    def formatted_name(self, obj):
        name_parts = [obj.last_name, obj.first_name]
        if obj.patronymic:
            name_parts.append(obj.patronymic)
        return format_html(
            '<span class="font-semibold text-primary-600">{}</span>',
            " ".join(name_parts)
        )
    
    @display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:backend_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.user.email
            )
        return "-"
    
    @display(
        description=_("Полный адрес"),
    )
    def full_address(self, obj):
        address_parts = []
        if obj.city:
            address_parts.append(obj.city)
        if obj.street:
            address_parts.append(obj.street)
        if obj.house:
            address_parts.append(f"д. {obj.house}")
        if obj.building:
            address_parts.append(f"к. {obj.building}")
        if obj.structure:
            address_parts.append(f"стр. {obj.structure}")
        if obj.apartment:
            address_parts.append(f"кв. {obj.apartment}")
        
        if address_parts:
            return format_html(
                '<span class="text-sm text-gray-600">{}</span>',
                ", ".join(address_parts)
            )
        return "-"


@admin.register(EmailConfirmToken)
class EmailConfirmTokenAdmin(ModelAdmin):
    list_display = (
        'formatted_id',
        'user_link',
        'token_preview',
        'is_expired_badge',
        'created_at',
        'expires_at',
    )
    list_filter = (
        ('created_at', RangeDateFilter),
        ('expires_at', RangeDateFilter),
    )
    search_fields = ('id', 'user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at')
    list_per_page = 25
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Основная информация"), {
            "fields": [
                "user",
                "token",
            ],
        }),
        (_("Временные метки"), {
            "classes": ["tab"],
            "fields": [
                ("created_at", "expires_at"),
            ],
        }),
    )
    
    @display(
        description=_("ID"),
        ordering="id",
    )
    def formatted_id(self, obj):
        return format_html(
            '<span class="font-semibold text-primary-600">#{}</span>',
            obj.id
        )
    
    @display(
        description=_("Пользователь"),
        ordering="user__email",
    )
    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:backend_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}" class="text-primary-600 hover:text-primary-800">{}</a>',
                url, obj.user.email
            )
        return "-"
    
    @display(
        description=_("Токен"),
    )
    def token_preview(self, obj):
        preview = obj.token[:16] + "..." if len(obj.token) > 16 else obj.token
        return format_html(
            '<span class="font-mono text-sm text-gray-600">{}</span>',
            preview
        )
    
    @display(
        description=_("Истек"),
        ordering="expires_at",
        label={
            True: "danger",
            False: "success",
        },
    )
    def is_expired_badge(self, obj):
        return obj.is_expired, "Истек" if obj.is_expired else "Активен"


# Настройки админки
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Netology Shop Admin')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Netology Shop Admin Portal')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Welcome to Netology Shop Admin Portal')

# Настройка logout redirect для админки
admin.site.logout_template = 'admin/logout.html'

