from rest_framework import serializers

from mainapp.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Категории"""

    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """Товары"""

    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'
