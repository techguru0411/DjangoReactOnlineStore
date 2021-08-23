from rest_framework import serializers

from mainapp.models import CartProduct, Cart, Customer
from eshop_api.main.serializers_main import ProductSerializer


class CartProductSerializer(serializers.ModelSerializer):
    """Товары для корзины"""

    product = ProductSerializer()

    class Meta:
        model = CartProduct
        fields = ['id', 'product', 'qty', 'final_price']


class CustomerSerializer(serializers.ModelSerializer):
    """Пользователи"""

    my_user = serializers.SerializerMethodField()

    @staticmethod
    def get_my_user(obj):
        first_name, last_name = obj.user.first_name, obj.user.last_name
        if not (first_name and last_name):
            return obj.user.username
        return ' '.join([first_name, last_name])

    class Meta:
        model = Customer
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    """Корзина"""
    # many=True для полей m2m
    products = CartProductSerializer(many=True)
    owner = CustomerSerializer()

    class Meta:
        model = Cart
        fields = '__all__'
