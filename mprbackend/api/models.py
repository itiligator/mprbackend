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
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

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
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager')
    processed = models.CharField(max_length=200, null=True, blank=True)
    invoice = models.CharField(max_length=200, null=True, blank=True)
    status = models.SmallIntegerField(default=-1)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)
    delivery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.date) + ' ' + self.manager.first_name + ' ' + self.manager.last_name + ' в ' + self.client_INN

    def to_dict(self):
        result = {
            'UUID': self.UUID,
            'clientINN': self.client_INN,
            'dataBase': self.database,
            'status': self.status,
            'managerID': self.manager.userprofile.manager_ID,
            'author': self.author.userprofile.manager_ID,
            'id': self.pk
        }
        if self.date:
            result['date'] = self.date
        if self.delivery_date:
            result['deliveryDate'] = self.delivery_date
        if self.payment:
            result['payment'] = self.payment
        if self.payment_plan:
            result['paymentPlan'] = self.payment_plan
        if self.processed:
            result['processed'] = self.processed
        if self.invoice:
            result['invoice'] = self.invoice

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
            self.database = data['dataBase']

        if 'invoice' in data:
            self.invoice = data['invoice']

        if 'processed' in data:
            self.processed = data['processed']

        if 'status' in data:
            self.status = int(data['status'])

        if 'managerID' in data:
            self.manager = User.objects.get(userprofile__manager_ID=data['managerID'])

        if ('author' in data) and data['author']:
            self.author = User.objects.get(userprofile__manager_ID=data['author'])

        if 'date' in data:
            self.date = data['date']

        if 'deliveryDate' in data:
            self.delivery_date = data['deliveryDate']

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
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)


class ChecklistQuestion(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_type = models.CharField(max_length=200)
    text = models.TextField()
    active = models.BooleanField(default=True)
    section = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    def __str__(self):
        return '"' + self.text + '" в разделе "' + self.section + '" для клиентов "' + self.client_type + '" ' + str(
            self.UUID)


class ChecklistAnswer(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ChecklistQuestion, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE)
    answer1 = models.TextField(blank=True)
    answer2 = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    class Meta:
        unique_together = [['visit', 'question']]
        order_with_respect_to = 'visit'

    def to_dict(self):
        result = {
            'UUID': self.UUID,
            'questionUUID': self.question.UUID,
            'visitUUID': self.visit.UUID
        }
        if self.answer1:
            result['answer1'] = self.answer1
        if self.answer2:
            result['answer2'] = self.answer2
        return result


class Client(models.Model):
    name = models.CharField(max_length=200)
    INN = models.CharField(max_length=12, unique=True)
    client_type = models.CharField(max_length=100, blank=True, null=True)
    price_type = models.CharField(max_length=100, blank=True, null=True)
    delay = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    authorized_managers = models.ManyToManyField(User, blank=True, related_name='authorized_managers')
    address = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING, related_name='clientmanager')
    status = models.BooleanField(default=True)
    database = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    def __str__(self):
        return self.name
    # TODO: сделать проверку корректности и исправление заполнения мнеджеров
    # def save(self, *args, **kwargs):  # если менеджер не указан явно, то назначаем первого попавшегося из
    #     # authorized_managers
    #     if not self.manager and self.authorized_managers.all().count() > 0 and 'manager' not in kwargs:
    #         self.manager = self.authorized_managers.all()[0]
    #     if self.manager not in self.authorized_managers.all():
    #         self.authorized_managers.add(self.manager)
    #     super().save(*args, **kwargs)

    def to_dict(self):
        res = {
            'name': self.name,
            'inn': self.INN,
            'clientType': self.client_type,
            'priceType': self.price_type,
            'delay': self.delay,
            'limit': self.limit,
            'authorizedManagersID': list(
                self.authorized_managers.all().values_list('userprofile__manager_ID', flat=True)),
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'dataBase': self.database,
            'manager': None if not self.manager else self.manager.userprofile.manager_ID
        }
        return {
            k: v
            for k, v in res.items()
            if v is not None
        }

    def update_from_dict(self, data):
        if 'dataBase' in data:
            self.database = data['dataBase']

        if 'status' in data:
            self.status = data['status']

        if 'name' in data:
            self.name = data['name']

        if 'inn' in data:
            self.inn = data['inn']

        if 'clientType' in data:
            self.client_type = data['clientType']

        if 'priceType' in data:
            self.price_type = data['priceType']

        if 'delay' in data:
            self.delay = data['delay']

        if 'limit' in data:
            self.limit = data['limit']

        if 'address' in data:
            self.address = data['address']

        if 'email' in data:
            self.email = data['email']

        if 'phone' in data:
            self.phone = data['phone']

        if 'manager' in data:
            self.manager = User.objects.get(userprofile__manager_ID=data['manager'])

        if 'authorizedManagersID' in data:
            managers = User.objects.filter(userprofile__manager_ID__in=data['authorizedManagersID'])
            self.authorized_managers.set(managers)

        self.save()


# @receiver(post_save, sender=Client)
# def complete_managers_relations(instance, **kwargs):
#     print('before all')
#     print(instance.authorized_managers.all())
#     print(instance.manager)
#     if not instance.manager and instance.authorized_managers.all().count() > 0 and 'manager' not in kwargs:
#         print('in add manager from authorized')
#         instance.manager = instance.authorized_managers.all()[0]
#         instance.save()
#         return
#     if instance.manager not in instance.authorized_managers.all():
#         print('in add manager to authorized')
#         print(instance.authorized_managers.all())
#         print(instance.manager)
#         instance.authorized_managers.add(instance.manager)
#         print(instance.authorized_managers.all())
#         print(instance.manager)
#         print(instance.authorized_managers.all())
#         print(instance.manager)
#         return

def photo_path(instance, filename):
    return '/'.join(['photos', instance.visit.client_INN, filename])


class Photo(models.Model):
    visit = models.ForeignKey(Visit, null=True, blank=True, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to=photo_path)
    timestamp = models.DateTimeField(auto_now=True)


class Task(models.Model):
    UUID = models.CharField(max_length=36, default=uuid.uuid4(), unique=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
    text = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now=True, editable=False, null=False, blank=False)

    def to_dict(self):
        result = {
            'UUID': self.UUID,
            'id': self.id,
            'manager': self.manager.userprofile__manager_ID,
            'text': self.text,
            'title': self.title,
            'deadline': self.deadline,
            'status': self.status
        }
        result = {k: v for k, v in result if v is not None}
        return result

    def update_from_dict(self, data):
        if 'text' in data:
            self.text = data['text']

        if 'title' in data:
            self.title = data['title']

        if 'manager' in data:
            self.manager = User.objects.get(userprofile__manager_ID=data['manager'])

        if 'deadline' in data:
            self.deadline = data['deadline']

        if 'status' in data:
            self.status = data['status']
