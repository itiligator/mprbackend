from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# временные предположения относительно уникальных идентификаторов и типов, получаемых в данных от 1С:
# manager_ID: перечисление от 1 до N
# client_ID: перечисление от 1 до N
# product_item: перечисление от 1 до N
# client_type: перечисление от 1 до N
# price_type: перечисление от 1 до N
# visit.status: 0 - не начат, 1 - в работе, 2 - завершен
# иные предположения:
# роли пользователей: "MPR", "OFFICE", "1S"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20)
    manager_ID = models.CharField(max_length=200, null=True, blank=True, unique=True)

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
    date = models.DateField(null=True, blank=True)
    database = models.BooleanField(default=True, null=True, blank=True)
    client_INN = models.CharField(max_length=200)
    payment = models.FloatField(null=True, blank=True)
    payment_plan = models.FloatField(null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)
    invoice = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=-1)

    def __str__(self):
        return str(self.date) + ' ' + self.manager.first_name + ' ' + self.manager.last_name + ' в ' + self.client_INN
    
    def to_dict(self):
        result = {
            'UUID': self.UUID,
            'clientINN': self.client_INN,
            'dataBase': self.database,
            'processed': self.processed,
            'status': self.status,
            'invoice': self.invoice,
            'managerID': self.manager.userprofile.manager_ID
        }
        if self.date:
            result['date'] = self.date
        if self.payment:
            result['payment'] = self.payment
        if self.payment_plan:
            result['paymentPlan'] = self.payment_plan

        orders = Order.objects.filter(visit=self)
        orders_array = [{
            'productItem': o.product_item,
            'order': o.order,
            'delivered': o.delivered,
            'recommend': o.recommend,
            'balance': o.balance,
            'sales': o.sales
        } for o in orders]
        result['orders'] = orders_array
        return result

    def update_from_dict(self, data):
        if 'dataBase' in data:
            if data['dataBase'] == 'true':
                self.database = True
            elif data['dataBase'] == 'false':
                self.database = False

        if 'invoice' in data:
            if data['invoice'] == 'true':
                self.invoice = True
            elif data['invoice'] == 'false':
                self.invoice = False

        if 'processed' in data:
            if data['processed'] == 'true':
                self.processed = True
            elif data['processed'] == 'false':
                self.processed = False

        if 'status' in data:
            self.status = int(data['status'])

        if 'managerID' in data:
            self.manager = User.objects.get(userprofile__manager_ID=data['managerID'])

        if 'date' in data:
            self.date = data['date']

        if 'payment' in data:
            self.payment = int(data['payment'])

        if 'paymentPlan' in data:
            self.payment_plan = int(data['paymentPlan'])

        if 'clientINN' in data:
            self.client_INN = data['clientINN']

        self.save()

        if 'orders' in data:
            orders = data['orders']
            for o in orders:
                try:
                    dbo = Order.objects.get(visit=self, product_item=o['productItem'])
                except Order.DoesNotExist:
                    dbo = Order(visit=self, product_item=o['productItem'])
                if 'order' in o:
                    dbo.order = int(o['order'])
                if 'sales' in o:
                    dbo.order = int(o['sales'])
                if 'delivered' in o:
                    dbo.order = int(o['delivered'])
                if 'recommend' in o:
                    dbo.order = int(o['recommend'])
                if 'balance' in o:
                    dbo.order = int(o['balance'])
                dbo.save()


class Order(models.Model):
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True)
    product_item = models.CharField(max_length=200)
    order = models.SmallIntegerField(null=True, blank=True, default=0)
    delivered = models.SmallIntegerField(null=True, blank=True, default=0)
    recommend = models.SmallIntegerField(null=True, blank=True, default=0)
    balance = models.SmallIntegerField(null=True, blank=True, default=0)
    sales = models.SmallIntegerField(null=True, blank=True, default=0)

class ChecklistQuestion(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_type = models.CharField(max_length=200)
    text = models.TextField
    active = models.BooleanField(default=True)


class ChecklistAnswer(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ChecklistQuestion, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    answer1 = models.TextField
    answer2 = models.TextField
