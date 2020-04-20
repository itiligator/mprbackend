from django.urls import path
from . import views

urlpatterns = [
    path('products', views.productsjson, name='productsjson'),
    path('clients', views.clientsjson, name='clientsjson'),
    path('orderlist', views.orderlist, name='orderlist'),
    path('getorder/<int:pk>', views.getorder, name='getorder'),
    path('putorder', views.putorder, name='putorder'),
]
