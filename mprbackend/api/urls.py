from django.urls import path
from . import views

urlpatterns = [
    path('products', views.products, name='products'),
    path('prices', views.prices, name='prices'),
    path('users', views.users, name='users'),
    path('clients', views.clients, name='clients'),
    path('visits', views.visits, name='visits'),
    path('resetvisits', views.resetvisits, name='resetvisits'),
    path('visits/<uuid:vuuid>', views.visit, name='visit'),
    path('checklistsquestions', views.checklistsquestions, name='checklistsquestions'),
    path('checklistsquestions/<uuid:quuid>', views.checklistsquestions, name='checklistsquestions'),
    path('checklistanswers', views.checklistanswers, name='checklistanswers'),
    path('users/me', views.usersme, name='usersme'),
]

