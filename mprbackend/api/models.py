from django.conf import settings
from django.db import models
import random


class ClientType(models.Model):
    HORECA = 'HC'
    STORE = 'ST'
    DRAFT = 'DR'

    TYPE = (
        (HORECA, 'Хорека'),
        (STORE, 'Магазин'),
        (DRAFT, 'Драфт'),
    )
    client_type = models.CharField(max_length=2, choices=TYPE, default=STORE)

    def name(self):
        return dict(self.TYPE)[str(self.client_type)]

    def __str__(self):
        return self.name()


class PriceType(models.Model):
    HORECA = 'HC'
    DRAFT = 'DR'
    MARCHENKO = 'MR'
    HORECA_ACTION = 'HA'
    DRAFT_ACTION = 'DA'

    TYPE = (
        (HORECA, 'Хорека'),
        (DRAFT, 'Драфт'),
        (HORECA_ACTION, 'Акция Хорека'),
        (DRAFT_ACTION, 'Акция Драфт'),
        (MARCHENKO, 'Марченко'),

    )
    price_type = models.CharField(max_length=2, choices=TYPE, default=HORECA)

    def name(self):
        return dict(self.TYPE)[str(self.price_type)]

    def __str__(self):
        return self.name()


class Client(models.Model):
    name = models.CharField(max_length=200)
    inn = models.CharField(max_length=12)
    client_type = models.ForeignKey(ClientType, on_delete=models.CASCADE)
    price_type = models.ForeignKey(PriceType, on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Visit(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    actual_date = models.DateField(auto_now_add=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.FloatField(default=0)


class Product(models.Model):
    item = models.IntegerField(unique=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100)

    def __str__(self):
        return 'А:' + str(self.item) + ' ' + str(self.name)


class Price(models.Model):
    price_type = models.ForeignKey(PriceType, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        unique_together = ('price_type', 'product',)

    def __str__(self):
        return str(self.value) + ' за ' + self.product.name + ' для ' + self.price_type.name()


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_date = models.DateField()
    delivery_date = models.DateField()
    processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        for product in Product.objects.all():
            oi = OrderItem.objects.create(product=product, quantity=0, order=self)

    def __str__(self):
        return 'Заказ от ' + str(self.creation_date) + ' для ' + str(self.client) + ' к ' + str(self.delivery_date)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('order', 'product',)

    def __str__(self):
        return str(self.quantity) + ' шт. ' + str(self.product.name) + ' для ' \
               + str(self.order.client.name) + 'в заказе от ' + str(self.order.creation_date)
