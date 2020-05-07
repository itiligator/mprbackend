from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# временные предположения относительно уникальных идентификаторов и типов, получаемых в данных от 1С:
# manager_ID: перечисление от 1 до N
# client_ID: перечисление от 1 до N
# product_item: перечисление от 1 до N
# client_type: перечисление от 1 до N
# price_type: перечисление от 1 до N
# иные предположения:
# роли пользователей: "MPR", "OFFICE", "1S"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20)
    manager_ID = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        onesid = (', ID в 1С: ' + self.manager_ID if self.manager_ID else "")
        return self.user.first_name + ' ' + self.user.last_name + ', роль: ' + self.role + onesid


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()


class Visit(models.Model):
    UUID = models.CharField(max_length=36)
    date = models.DateField()
    database = models.BooleanField(default=True)
    client_INN = models.CharField(max_length=200)
    payment = models.FloatField(null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)
    invoice = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=-1)


class Order(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True)
    product_item = models.CharField(max_length=200)
    order = models.SmallIntegerField(null=True, blank=True, default=0)
    delivered = models.SmallIntegerField(null=True, blank=True, default=0)
    recommend = models.SmallIntegerField(null=True, blank=True, default=0)
    balance = models.SmallIntegerField(null=True, blank=True, default=0)
    sales = models.SmallIntegerField(null=True, blank=True, default=0)

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
