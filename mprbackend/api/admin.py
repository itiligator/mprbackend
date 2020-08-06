from django.contrib import admin
from .models import Order, Visit, UserProfile, ChecklistAnswer, ChecklistQuestion, Client, Photo, Price

admin.site.register(Order)
admin.site.register(Visit)
admin.site.register(UserProfile)
admin.site.register(ChecklistQuestion)
admin.site.register(ChecklistAnswer)
admin.site.register(Client)
admin.site.register(Photo)
admin.site.register(Price)
