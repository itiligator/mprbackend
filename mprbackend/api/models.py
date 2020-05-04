from django.conf import settings
from django.db import models


# временные предположения относительно уникальных идентификаторов и типов, получаемых в данных от 1С:
# manager_ID: перечисление от 1 до N
# client_ID: перечисление от 1 до N
# product_item: перечисление от 1 до N
# client_type: перечисление от 1 до N
# price_type: перечисление от 1 до N
# иные предположения:
# роли пользователей: "MPR" или "OFFICE"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20)
    manager_ID = models.CharField(max_length=200)


class Visit(models.Model):
    UUID = models.CharField(max_length=36)
    date = models.DateField()
    database = models.BooleanField(default=True)
    client_ID = models.CharField(max_length=200)
    payment = models.FloatField(default=-1)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=-1)


class Order(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True)
    product_item = models.CharField(max_length=200)
    ordered_quantity = models.SmallIntegerField(default=-1)
    delivered_quantity = models.SmallIntegerField(default=-1)
    recommended_quantity = models.SmallIntegerField(default=-1)
    stock_quantity = models.SmallIntegerField(default=-1)

# class ClientType(models.Model):
#     HORECA = 'HC'
#     STORE = 'ST'
#     DRAFT = 'DR'
#
#     TYPE = (
#         (HORECA, 'Хорека'),
#         (STORE, 'Магазин'),
#         (DRAFT, 'Драфт'),
#     )
#     client_type = models.CharField(max_length=2, choices=TYPE, default=STORE)
#
#     def name(self):
#         return dict(self.TYPE)[str(self.client_type)]
#
#     def __str__(self):
#         return self.name()


# class PriceType(models.Model):
#     HORECA = 'HC'
#     DRAFT = 'DR'
#     MARCHENKO = 'MR'
#     HORECA_ACTION = 'HA'
#     DRAFT_ACTION = 'DA'
#
#     TYPE = (
#         (HORECA, 'Хорека'),
#         (DRAFT, 'Драфт'),
#         (HORECA_ACTION, 'Акция Хорека'),
#         (DRAFT_ACTION, 'Акция Драфт'),
#         (MARCHENKO, 'Марченко'),
#
#     )
#     price_type = models.CharField(max_length=2, choices=TYPE, default=HORECA)
#
#     def name(self):
#         return dict(self.TYPE)[str(self.price_type)]
#
#     def __str__(self):
#         return self.name()


# class Client(models.Model):
#     client_ID = models.CharField(max_length=100)
#     name = models.CharField(max_length=200)
#     inn = models.CharField(max_length=12)
#     client_type = models.CharField(max_length=20)
#     price_type = models.CharField(max_length=20)
#     managers = models.ManyToManyField(settings.AUTH_USER_MODEL)
#     email = models.CharField(max_length=200)
#     phone = models.CharField(max_length=200)
#     longitude = models.CharField(max_length=200)
#     latitude = models.CharField(max_length=200)
#     status = models.BooleanField(default=True)
#     database = models.BooleanField(default=True)
#
#     def __str__(self):
#         return self.name


# class Product(models.Model):
#     item = models.IntegerField(unique=True)
#     name = models.CharField(max_length=40)
#     description = models.CharField(max_length=100)
#
#     def __str__(self):
#         return 'А:' + str(self.item) + ' ' + str(self.name)


# class Price(models.Model):
#     price_type = models.CharField(max_length=200)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     value = models.FloatField()
#     database = models.BooleanField(default=True)
#
#     # class Meta:
#     #     unique_together = ('price_type', 'product',)
#
#     def __str__(self):
#         return str(self.value) + ' за ' + self.product.name + ' для ' + self.price_type


# class Order(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     creation_date = models.DateField()
#     delivery_date = models.DateField()
#     processed = models.BooleanField(default=False)
#
#     def save(self, *args, **kwargs):
#         super(Order, self).save(*args, **kwargs)
#         for product in Product.objects.all():
#             oi = OrderItem.objects.create(product=product, quantity=0, order=self)
#
#     def __str__(self):
#         return 'Заказ от ' + str(self.creation_date) + ' для ' + str(self.client) + ' к ' + str(self.delivery_date)
#
