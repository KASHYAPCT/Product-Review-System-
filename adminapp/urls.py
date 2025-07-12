from django.urls import path
from .views import *


urlpatterns = [
    path('admincreate/', AdminCreate.as_view(), name="AdminCreate"),
    path('login/',Login.as_view(),name="login"),
    path('regularusercreate/', RegularUserCreate.as_view(), name="RegularUserCreate"),
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('products/<int:product_id>/reviews/', ReviewListCreate.as_view(), name='product-reviews'),
]


