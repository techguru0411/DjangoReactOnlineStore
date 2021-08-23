from rest_framework import routers

from eshop_api.cart.views_cart import CartViewSet

# Альтернатива регистрации path, используется для классов
# наследуемых от ViewSet
router = routers.SimpleRouter()
router.register('cart', CartViewSet, basename='cart')

# Добавление марщрутов
urlpatterns = []
urlpatterns += router.urls
