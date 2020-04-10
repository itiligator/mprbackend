from django.contrib import admin
from .models import PriceType, ClientType, Product, Price, Client

admin.site.register(PriceType)
admin.site.register(ClientType)
admin.site.register(Product)
admin.site.register(Price)
admin.site.register(Client)