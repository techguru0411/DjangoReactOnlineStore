import json

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    """Категории"""

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    @property
    def products(self):
        """Получить все товары относящиеся к данной категории"""
        return json.dumps(Product.objects.filter(category=self).values())

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    """Товары"""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name='Категория')
    title = models.CharField(max_length=255, verbose_name='Наименование')
    description = models.TextField(
        max_length=10000, null=True, verbose_name='Описание')
    image = models.ImageField(
        upload_to='mainapp/products/', verbose_name='Изображение')
    price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Цена')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class CartProduct(models.Model):
    """Товар для корзины. Промежуточная модель"""

    user = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, verbose_name='Покупатель')
    cart = models.ForeignKey(
        'Cart', on_delete=models.CASCADE, related_name='related_products',
        verbose_name='Корзина')
    qty = models.PositiveIntegerField(
        default=1, verbose_name='Количество товара')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name='Товар')
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Продукт: {self.product.title} (для корзины)'

    class Meta:
        verbose_name = 'Товар для корзины'
        verbose_name_plural = 'Товары для корзины'


class Cart(models.Model):
    """Корзина"""

    owner = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, null=True,
        verbose_name='Владелец')
    products = models.ManyToManyField(
        CartProduct, related_name='related_cart', blank=True)
    total_products = models.PositiveSmallIntegerField(default=0)
    final_price = models.DecimalField(
        max_digits=9, decimal_places=2, default=0, verbose_name='Общая цена')
    in_order = models.BooleanField(
        default=False, verbose_name='Корзина используется')
    for_anonymous_user = models.BooleanField(
        default=False, verbose_name='Пользователь авторизован')

    def save(self, *args, **kwargs):
        """Обновляем информацию о корзине при сохранении"""
        if self.id:  # если корзина существует
            self.total_products = self.products.count()
            self.final_price = sum(
                [cproduct.final_price for cproduct in self.products.all()])
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class Customer(models.Model):
    """Профиль пользователя"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='Номер телефона')
    address = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Адрес')

    def __str__(self):
        if not (self.user.first_name and self.user.last_name):
            return self.user.username
        return f'Покупатель: {self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
