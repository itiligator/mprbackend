from django.contrib import admin
from .models import PriceType, ClientType, Product, Price, Client, OrderItem, Order

admin.site.register(PriceType)
admin.site.register(ClientType)
admin.site.register(Product)
admin.site.register(Price)
admin.site.register(Client)
admin.site.register(Order)
admin.site.register(OrderItem)
