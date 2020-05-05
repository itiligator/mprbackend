import os
from django.contrib.auth.models import User
import jsonschema
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

from .models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

import json

from django.conf import settings

products_path = os.path.join(settings.BASE_DIR, "static", "products.json")
products_schema = {
    "type": "array",
    "items": {
        "title": "Товар",
        "type": "object",
        "description": "Товары пивоварни",
        "properties": {
            "item": {
                "type": [
                    "string",
                    "integer"
                ],
                "description": "Артикул товара"
            },
            "name": {
                "type": "string",
                "description": "Короткое наименование товара"
            },
            "description": {
                "type": "string",
                "description": "Развернутое описание товара"
            }
        },
        "required": [
            "item",
            "name",
            "description"
        ]
    }
}

prices_path = os.path.join(settings.BASE_DIR, "static", "prices.json")
prices_schema = {
    "type": "array",
    "items": {
        "title": "Цена",
        "type": "object",
        "description": "Цена данного типа для товара ",
        "x-tags": [
            "1С",
            "Офис",
            "Фронтенд"
        ],
        "properties": {
            "productItem": {
                "type": "string",
                "description": "Артикул товара"
            },
            "priceType": {
                "type": "string",
                "description": "Тип цены"
            },
            "amount": {
                "type": "string",
                "description": "Величина в рублях"
            },
            "database": {
                "type": "boolean"
            }
        },
        "required": [
            "productItem",
            "priceType",
            "amount",
            "database"
        ]
    }
}

clients_path = os.path.join(settings.BASE_DIR, "static", "clients.json")
clients_schema = {
    "type": "array",
    "items": {
        "title": "Клиент",
        "type": "object",
        "description": "Данные клиента",
        "x-examples": {},
        "properties": {
          "clientID": {
            "type": "string",
            "description": "Уникальный идентификатор клиента"
          },
          "name": {
            "type": "string",
            "description": "Наименование клиента для отображения пользователю"
          },
          "inn": {
            "type": "string",
            "description": "ИНН"
          },
          "clientType": {
            "type": "string",
            "description": "Тип клиента (хорека, драфт, магазин etc)"
          },
          "priceType": {
            "type": "string",
            "description": "Тип цен для клиента"
          },
          "delay": {
            "type": "integer",
            "default": 0,
            "description": "Отсрочка по договору",
            "format": "int32",
            "example": 0,
            "minimum": 0,
            "maximum": 45
          },
          "limit": {
            "type": "integer",
            "default": 0,
            "description": "Лимит",
            "format": "int64",
            "example": 0,
            "minimum": 0,
            "maximum": 100000
          },
          "authorizedManagersID": {
            "type": "array",
            "description": "Массив ID менеджеров, для которых доступен клиент",
            "items": {
              "type": "string"
            }
          },
          "email": {
            "type": "string",
            "format": "email"
          },
          "phone": {
            "type": "string"
          },
          "manager": {
            "type": "string"
          },
          "longitude": {
            "type": "string"
          },
          "latitude": {
            "type": "string"
          },
          "status": {
            "type": "boolean",
            "default": "1",
            "description": "Действует/не действует"
          },
          "dataBase": {
            "type": "boolean",
            "default": "0"
          }
        },
        "required": [
          "clientID",
          "name",
          "clientType",
          "priceType",
          "delay",
          "authorizedManagersID",
          "status",
          "dataBase"
        ]
      },
}

# TODO: переписать функции. DRY!
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def products(request):
    if request.method == 'GET':
        try:
            with open(products_path, 'r', encoding="utf-8") as f:
                json_data = json.loads(f.read())
                return JsonResponse(json_data, safe=False)
        except FileNotFoundError:
            return Response('No such file, please upload it first', status=status.HTTP_503_SERVICE_UNAVAILABLE)
    elif request.method == 'POST':
        if request.user.userprofile.role != '1S':
            return Response("Only 1S can do it", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                jsonschema.validate(instance=request.data, schema=products_schema)
            except jsonschema.exceptions.ValidationError:
                return Response('JSON data validation failed', status=status.HTTP_400_BAD_REQUEST)
            with open(products_path, 'w', encoding="utf-8") as f:
                json.dump(request.data, f, ensure_ascii=False)
            return Response('Product list have been saved', status=status.HTTP_200_OK)
    else:
        return Response('Method not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def prices(request):
    if request.method == 'GET':
        try:
            with open(prices_path, 'r', encoding="utf-8") as f:
                product_item = request.query_params.get('productItem')
                price_type = request.query_params.get('priceType')
                json_data = json.loads(f.read())
                if price_type:
                    json_data = [x for x in json_data if x['priceType'] == price_type]
                if product_item:
                    json_data = [x for x in json_data if x['productItem'] == product_item]
                return JsonResponse(json_data, safe=False)
        except FileNotFoundError:
            return Response('No such file, please upload it first', status=status.HTTP_503_SERVICE_UNAVAILABLE)
    elif request.method == 'POST':
        if request.user.userprofile.role != '1S':
            return Response("Only 1S can do it", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                jsonschema.validate(instance=request.data, schema=prices_schema)
            except jsonschema.exceptions.ValidationError:
                return Response('JSON data validation failed', status=status.HTTP_400_BAD_REQUEST)
            with open(prices_path, 'w', encoding="utf-8") as f:
                json.dump(request.data, f, ensure_ascii=False)
            return Response('Price list have been saved', status=status.HTTP_200_OK)
    else:
        return Response('Method not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.user.userprofile.role == 'MPR':
        data = {'firstName': request.user.first_name, 'lastName': request.user.last_name, 'ID': request.user.userprofile.manager_ID}
        return JsonResponse(data, safe=False)
    elif request.user.userprofile.role == 'OFFICE':
        users = User.objects.filter(userprofile__role='MPR')
        data = []
        for user in users:
            data.append({'firstName': user.first_name, 'lastName': user.last_name, 'ID': user.userprofile.manager_ID})
        return JsonResponse(data, safe=False)
    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def clients(request):
    if request.method == 'GET':
        try:
            with open(clients_path, 'r', encoding="utf-8") as f:
                print(request.query_params)
                client_id = request.query_params.get('ID')
                client_type = request.query_params.get('clientType')
                price_type = request.query_params.get('priceType')
                client_status = request.query_params.get('status')
                if request.user.userprofile.role == 'MPR':
                    manager = request.user.userprofile.manager_ID
                else:
                    manager = request.query_params.get('managerID')
                json_data = json.loads(f.read())
                if client_id:
                    json_data = [x for x in json_data if x['ID'] == client_id]
                if client_type:
                    json_data = [x for x in json_data if x['clientType'] == client_type]
                if price_type:
                    json_data = [x for x in json_data if x['priceType'] == price_type]
                if client_status:
                    json_data = [x for x in json_data if str(x['status']).lower() == client_status]
                if manager:
                    json_data = [x for x in json_data if manager in x['authorizedManagersID']]
                return JsonResponse(json_data, safe=False)
        except FileNotFoundError:
            return Response('No such file, please upload it first', status=status.HTTP_503_SERVICE_UNAVAILABLE)
    elif request.method == 'POST':
        if request.user.userprofile.role != '1S':
            return Response("Only 1S can do it", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                jsonschema.validate(instance=request.data, schema=clients_schema)
            except jsonschema.exceptions.ValidationError:
                return Response('JSON data validation failed', status=status.HTTP_400_BAD_REQUEST)
            with open(clients_path, 'w', encoding="utf-8") as f:
                json.dump(request.data, f, ensure_ascii=False)
            return Response('Client list have been saved', status=status.HTTP_200_OK)
    else:
        return Response('Method not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def productsjson(request):
#     products_dicts = [{'item': product.item, 'name': product.name, 'description': product.description,
#                        'price': {price.price_type.name(): price.value for price in
#                                  Price.objects.filter(product=product)}}
#                       for product in Product.objects.all()]
#     return JsonResponse(products_dicts, safe=False)
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def clientsjson(request):
#     clients_dicts = [{'pk': client.pk,
#                       'name': client.name,
#                       'inn': client.inn,
#                       'manager': client.manager.first_name + ' ' + client.manager.last_name,
#                       'client_type': client.client_type.name(),
#                       'price_type': client.price_type.name()}
#                      for client in Client.objects.filter(is_active=True)]
#
#     return JsonResponse(clients_dicts, safe=False)
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def orderlist(request):
#     orderlist_dicts = [
#         {'order_pk': order.pk,
#          'client_pk': order.client.pk,
#          'client_name': order.client.name,
#          'creation_date': order.creation_date,
#          'delivery_date': order.delivery_date,
#          'processed': order.processed}
#         for order in Order.objects.filter(manager=request.user).order_by('-creation_date')
#     ]
#
#     return JsonResponse(orderlist_dicts, safe=False)
#
#
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getorder(request, pk):
#     try:
#         order = Order.objects.get(pk=pk)
#     except Order.DoesNotExist:
#         return HttpResponseNotFound('<h1>Order not found</h1>')
#     order_dict = {
#         'order_pk': order.pk,
#         'client_pk': order.client.pk,
#         'client_name': order.client.name,
#         'creation_date': order.creation_date,
#         'delivery_date': order.delivery_date,
#         'processed': order.processed,
#         'orderitems': [{
#             'item': orderitem.product.item,
#             'name': orderitem.product.name,
#             'quantity': orderitem.quantity
#         } for orderitem in OrderItem.objects.filter(order=order)]
#     }
#     return JsonResponse(order_dict, safe=False)
#
#
# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def putorder(request):
#     try:
#         pk = int(request.data["order_pk"])  # PK заказа
#     except ValueError:
#         return Response({}, status=status.HTTP_400_BAD_REQUEST)  # если PK заказа невалидный
#
#     if pk != -1:  # если передан PK заказа отличный от -1, т.е. заказ уже существует
#
#         try:  # попытаться отыскать существующий заказ
#             order = Order.objects.get(pk=pk)
#         except Order.DoesNotExist:
#             return Response({}, status=status.HTTP_400_BAD_REQUEST)
#
#         if request.user != order.manager:  # если заказ создан другим пользователем, то вернуть ответ 401
#             return Response({}, status=status.HTTP_401_UNAUTHORIZED)
#
#         if order.processed:  # если заказ уже ушел в обработку
#             return Response({}, status=status.HTTP_304_NOT_MODIFIED)
#
#     else:  # если PK заказа -1, т.е. должен быть создан новый заказ
#         try:
#             client_pk = int(request.data["client_pk"])
#             client = Client.objects.get(pk=client_pk)
#             order = Order.objects.create(
#                 client=client,
#                 manager=request.user,
#                 creation_date=timezone.now(),
#                 delivery_date=timezone.now(),
#             )  # TODO: сделать таки установку даты доставки заказа
#
#         except (ValueError, Client.DoesNotExist):
#             return Response({}, status=status.HTTP_400_BAD_REQUEST)
#
#     orderitems = OrderItem.objects.filter(order=order)  # QuerySet существующих элементов заказа
#     req_orderitems = request.data['orderitems']  # словарь принятых элементов заказа
#
#     for item in req_orderitems:  # обход словаря принятых элементов заказа
#
#         try:  # попытаться отыскать в базе элемент заказа соответствующий принятому элементу
#             orderitem = orderitems.get(product__pk=req_orderitems[item]['item'])
#         except (OrderItem.DoesNotExist, KeyError):  # если таковой не найден
#             try:  # попытаться отыскать в базе соответствующий элементу заказа продукт и создать элемент заказа
#                 req_product = Product.objects.get(pk=req_orderitems[item]['item'])
#                 orderitem = OrderItem.objects.create(order=order, product=req_product, quantity=0)
#             except (Product.DoesNotExist, KeyError):  # если продукт не найден, то вернуть 400
#                 return Response({}, status=status.HTTP_400_BAD_REQUEST)
#
#         # TODO: сделать таки установку даты доставки заказа
#
#         orderitem.quantity = req_orderitems[item]['quantity']  # присвоить новое количество продукта в элементе
#         orderitem.save()  # заказа и сохранить этот элемент
#
#     if pk != 1:
#         return Response({}, status=status.HTTP_200_OK)
#     else:
#         return Response({}, status=status.HTTP_201_CREATED)
