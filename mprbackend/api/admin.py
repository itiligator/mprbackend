from django.contrib import admin
from .models import Order, Visit, UserProfile, ChecklistAnswer, ChecklistQuestion

admin.site.register(Order)
admin.site.register(Visit)
admin.site.register(UserProfile)
admin.site.register(ChecklistQuestion)
admin.site.register(ChecklistAnswer)

