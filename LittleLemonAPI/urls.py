from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items/', views.MenuItems),
    path('menu-items/<int:id>/', views.SingleMenuItems),
    path('category/', views.categories),
    path('groups/manager/users/', views.managers),
    path('groups/manager/users/<int:id>/', views.SingleManagerView),
    path('groups/delivery-crew/users/', views.DeliveryCrew),
    path('groups/delivery-crew/users/<int:id>/', views.SingleDeliveryCrew),
    path('api-token-auth/', obtain_auth_token),
    path('cart/menu-items/', views.ViewCart),
    path('orders/', views.ViewOrder),
    path('orders/<int:id>/', views.OrderSummary),
]
