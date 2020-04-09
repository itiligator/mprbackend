from django.conf import settings
from django.db import models


class ClientType(models.Model):
    type = models.CharField(max_length=2)

    def __str__(self):
        return self.type


class Client(models.Model):
    name = models.CharField(max_length=200)
    inn = models.CharField(max_length=12, unique=True)
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    manager = models.CharField(max_length=200)
    is_active = models.BooleanField()

    def __str__(self):
        return self.name


class Visit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    actual_date = models.DateField(auto_now_add=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.FloatField(default=0)


class Product(models.Model):
    item = models.IntegerField(unique=True)
    description = models.CharField(max_length=100)
    name = models.CharField(max_length=40)

    def __str__(self):
        return 'А: ' + str(self.item) + ' ' + str(self.name)


class Price(models.Model):
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        unique_together = ('client_type', 'product', )

    def __str__(self):
        return str(self.value) + ' за ' + self.product.name + ' для ' + self.client_type.name


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)
    delivery_date = models.DateField()
    processed = models.BooleanField(default=False)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

