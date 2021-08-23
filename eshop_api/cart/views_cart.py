from rest_framework import viewsets, response, status
from rest_framework.decorators import action

from django.shortcuts import get_object_or_404

from mainapp.models import Product, CartProduct, Cart, Customer
from .serializers_cart import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    """Корзина"""
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    @staticmethod
    def get_cart(user):
        """
        Получить правильную корзину на основании
        текущего пользователя - self.request.user
        """
        if user.is_authenticated:
            return Cart.objects.filter(
                owner=user.customer, for_anonymous_user=False).first()
        return Cart.objects.filter(for_anonymous_user=True).first()

    @staticmethod
    def _get_or_create_cart_product(customer: Customer,
                                    cart: Cart,
                                    product: Product):
        """Получить или создать CartProduct для конкретной корзины"""
        cart_product, created = CartProduct.objects.get_or_create(
            user=customer, product=product, cart=cart
        )
        return cart_product, created

    """
    Иной способ простроения маршрутов, через декоратор '@action'. Имя метода
    добавляем к маршруту т.е. http://127.0.0.1:8000/api/cart/ +
    current_customer_cart/ для ф-ии ниже. Определяем работу методов viewsets,
    detail=False - не используем конкретный объект,
    url_path='current_cu... - итоговый endpoin для того что бы метод работал
    """

    @action(methods=['get'], detail=False)
    def current_customer_cart(self, *args, **kwargs):
        """Состояние корзины текущего пользователя"""
        cart = self.get_cart(self.request.user)
        cart_serializer = CartSerializer(cart)
        # Возврат сериализованных данных
        return response.Response(cart_serializer.data)

    @action(methods=['put'], detail=False,
            url_path='current_customer_cart/add_to_cart/(?P<product_id>\d+)')
    def product_add_to_card(self, *args, **kwargs):
        """Добавление товара в корзину"""
        cart = self.get_cart(self.request.user)
        product = get_object_or_404(Product, id=kwargs['product_id'])
        cart_product, created = self._get_or_create_cart_product(
            self.request.user.customer, cart, product)
        if created:
            cart.products.add(cart_product)
            cart.save()
            return response.Response({'detail': 'Товар добавлен в корзину'})
        return response.Response(
            {'detail': 'Товар уже в корзине'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['patch'], detail=False,
            url_path=('current_customer_cart/change_qty/(?P<qty>\d+)/'
                      '(?P<cart_product_id>\d+)'))
    def product_change_qty(self, *args, **kwargs):
        """Изменить кол-во товара"""
        cart_product = get_object_or_404(
            CartProduct, id=kwargs['cart_product_id'])
        cart_product.qty = int(kwargs['qty'])
        cart_product.save()
        cart_product.cart.save()  # для пересчёта корзины
        return response.Response(status=status.HTTP_200_OK)

    @action(methods=['put'], detail=False,
            url_path=('current_customer_cart/remove_from_cart/'
                      '(?P<cart_product_id>\d+)'))
    def product_remove_from_cart(self, *args, **kwargs):
        """Удалить продукт из корзины"""
        cart = self.get_cart(self.request.user)
        cart_product = get_object_or_404(
            CartProduct, id=kwargs['cart_product_id'])
        cart.products.remove(cart_product)
        cart_product.delete()
        cart.save()  # для пересчёта корзины
        return response.Response(status=status.HTTP_204_NO_CONTENT)
