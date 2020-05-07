import os
from django.contrib.auth.models import User
import jsonschema
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

from .models import Order, Visit
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
            "price_0": {
                "type": "string",
                "description": "Цена в рублях 2"
            },
            "price_1": {
                "type": "string",
                "description": "Цена в рублях 1"
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
                inn = request.query_params.get('inn')
                client_type = request.query_params.get('clientType')
                price_type = request.query_params.get('priceType')
                client_status = request.query_params.get('status')
                if request.user.userprofile.role == 'MPR':
                    manager = request.user.userprofile.manager_ID
                else:
                    manager = request.query_params.get('managerID')
                json_data = json.loads(f.read())
                if inn:
                    json_data = [x for x in json_data if x['inn'] == inn]
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


def visit_dict(pk):
    pass


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visits(request):
    if request.method == 'GET':
        # собираем в кучку параметры запроса
        # ВНИМАНИЕ! лютый говнокод
        # TODO: переписать по-человечески выборку из визитов
        manager = None
        if request.user.userprofile.role == 'MPR':
            manager = User.objects.get(userprofile__manager_ID=request.user.userprofile.manager_ID)
        else:
            managerID = request.query_params.get('managerID', None)
            if managerID:
                try:
                    manager = User.objects.get(userprofile__manager_ID=managerID)
                except User.DoesNotExist:
                    return Response({}, status=status.HTTP_204_NO_CONTENT)
        processed = request.query_params.get('processed', None)
        invoice = request.query_params.get('invoice', None)
        visit_status = request.query_params.get('status', None)
        client_inn = request.query_params.get('clientINN', None)
        date = request.query_params.get('date', None)
        # делаем последовательную фильтрацию
        # потому что https://docs.djangoproject.com/en/3.0/topics/db/queries/#querysets-are-lazy
        # и это ничего не стоит
        q = Visit.objects.all()
        if manager:
            q = q.filter(manager=manager)
        if processed:
            processed = True if (processed == "true" or processed == "True") else False
            q = q.filter(processed=processed)
        if invoice:
            invoice = True if (invoice == "true" or invoice == "True") else False
            q = q.filter(invoice=invoice)
        if visit_status:
            q = q.filter(status=visit_status)
        if client_inn:
            q = q.filter(client_INN=client_inn)
        if date:
            q = q.filter(date=date)
        print(len(q))

        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def visit(request, uuid):
    if request.method == 'GET':
        print(uuid)
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    elif request.method == 'PUT':
        return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
    return Response({}, status=status.HTTP_501_NOT_IMPLEMENTED)
